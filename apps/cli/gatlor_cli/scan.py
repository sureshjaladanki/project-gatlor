# SPDX-FileCopyrightText: 2026 Suresh Jaladanki
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import hashlib
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

from gatlor_evidence.checklist import render_checklist, run_checks
from gatlor_evidence.vex import VulnerabilityHit, write_in_triage_vex
from gatlor_ingest.parse import InvalidSbomError, parse_cyclonedx_json
from gatlor_vendors.osv import OsvClient, OsvQuery
from gatlor_vendors.syft import SyftNotFoundError

SyftFn = Callable[[Path], bytes]


class ScanError(RuntimeError):
    """The scan could not write its artifacts."""


def run_scan(
    *,
    scan_path: Path,
    out_dir: Path,
    repo_root: Path,
    osv_client: OsvClient,
    syft: SyftFn,
    sbom_path: Path | None = None,
    clock: Callable[[], datetime] | None = None,
) -> dict[str, Path]:
    now = (clock or (lambda: datetime.now(UTC)))()
    out_dir.mkdir(parents=True, exist_ok=True)
    if sbom_path is not None:
        raw_sbom = sbom_path.read_bytes()
    else:
        try:
            raw_sbom = syft(scan_path)
        except SyftNotFoundError as exc:
            raise ScanError(str(exc)) from exc
        except RuntimeError as exc:
            raise ScanError(str(exc)) from exc
    try:
        parsed = parse_cyclonedx_json(raw_sbom)
    except InvalidSbomError as exc:
        raise ScanError(f"SBOM is not valid CycloneDX JSON: {exc}") from exc
    queries = tuple(
        OsvQuery(purl=component.purl) for component in parsed.components if component.purl
    )
    try:
        osv_hits = osv_client.query_batch(queries)
    except (OSError, ValueError) as exc:
        raise ScanError(f"OSV query failed: {exc}") from exc
    hits = tuple(
        VulnerabilityHit(
            purl=hit.purl,
            vuln_id=hit.vuln_id,
            summary=hit.summary,
            aliases=hit.aliases,
        )
        for hit in osv_hits
    )
    vex_bytes = write_in_triage_vex(hits, product_name=parsed.name, generated_at=now)
    missing_purl = sum(1 for component in parsed.components if not component.purl)
    checks = run_checks(
        spec_version=parsed.spec_version,
        component_count=len(parsed.components),
        missing_purl_count=missing_purl,
        queried_purl_count=len(queries),
        hits=hits,
        repo_root=repo_root,
    )
    digest = hashlib.sha256(raw_sbom).hexdigest()
    checklist = render_checklist(checks, hits, generated_at=now, sbom_sha256=digest)
    written = {
        "sbom": out_dir / "sbom.cdx.json",
        "vex": out_dir / "vex.cdx.json",
        "checklist": out_dir / "readiness-checklist.md",
    }
    written["sbom"].write_bytes(raw_sbom)
    written["vex"].write_bytes(vex_bytes)
    written["checklist"].write_text(checklist, encoding="utf-8")
    return written
