# SPDX-FileCopyrightText: 2026 Suresh Jaladanki
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import re
from datetime import datetime
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from gatlor_evidence.claims import lint_text
from gatlor_evidence.vex import VulnerabilityHit

RULE_VERSION = "phase0-1"
SUPPORT_PERIOD_RE = re.compile(r"support_period_end:\s*(\d{4}-\d{2}-\d{2})")
EXPORT_NOTICE = (
    "This export is a record of evidence held in Gatlor. "
    "It is not a statement that the product meets the Cyber Resilience Act."
)


class CheckResult(StrEnum):
    PASS = "pass"
    FAIL = "fail"


class ReadinessCheck(BaseModel):
    model_config = ConfigDict(frozen=True)

    check_id: str
    result: CheckResult
    detail: str
    rule_version: str = RULE_VERSION


def run_checks(
    *,
    spec_version: str,
    component_count: int,
    missing_purl_count: int,
    queried_purl_count: int,
    hits: tuple[VulnerabilityHit, ...],
    repo_root: Path,
) -> tuple[ReadinessCheck, ...]:
    disclosure = repo_root / "SECURITY.md"
    support = repo_root / "SUPPORT.md"
    disclosure_text = disclosure.read_text(encoding="utf-8") if disclosure.is_file() else ""
    support_text = support.read_text(encoding="utf-8") if support.is_file() else ""
    support_match = SUPPORT_PERIOD_RE.search(support_text)
    claim_hits = lint_text(disclosure_text + "\n" + support_text)
    return (
        ReadinessCheck(
            check_id="sbom-present",
            result=CheckResult.PASS,
            detail=f"{component_count} components, CycloneDX {spec_version}",
        ),
        ReadinessCheck(
            check_id="sbom-cyclonedx",
            result=CheckResult.PASS,
            detail=f"specVersion {spec_version}",
        ),
        ReadinessCheck(
            check_id="component-purl",
            result=CheckResult.FAIL if missing_purl_count else CheckResult.PASS,
            detail=(
                f"{missing_purl_count} components have no purl"
                if missing_purl_count
                else "every component has a purl"
            ),
        ),
        ReadinessCheck(
            check_id="osv-match",
            result=CheckResult.PASS,
            detail=f"queried {queried_purl_count} purls, {len(hits)} matches",
        ),
        ReadinessCheck(
            check_id="vex-decided",
            result=CheckResult.FAIL if hits else CheckResult.PASS,
            detail=(
                f"{len(hits)} matches are in_triage; a named human must decide. "
                "The CLI does not decide."
                if hits
                else "no OSV matches"
            ),
        ),
        ReadinessCheck(
            check_id="disclosure-policy",
            result=CheckResult.PASS if disclosure.is_file() else CheckResult.FAIL,
            detail="SECURITY.md present" if disclosure.is_file() else "SECURITY.md missing",
        ),
        ReadinessCheck(
            check_id="support-period",
            result=CheckResult.PASS if support_match else CheckResult.FAIL,
            detail=(
                f"support_period_end {support_match.group(1)}"
                if support_match
                else "SUPPORT.md must contain support_period_end: YYYY-MM-DD"
            ),
        ),
        ReadinessCheck(
            check_id="claims-lint",
            result=CheckResult.FAIL if claim_hits else CheckResult.PASS,
            detail=(
                f"{len(claim_hits)} forbidden claim terms in SECURITY.md or SUPPORT.md"
                if claim_hits
                else "no forbidden claim terms in SECURITY.md or SUPPORT.md"
            ),
        ),
    )


def render_checklist(
    checks: tuple[ReadinessCheck, ...],
    hits: tuple[VulnerabilityHit, ...],
    *,
    generated_at: datetime,
    sbom_sha256: str,
) -> str:
    rows = "\n".join(
        f"| `{check.check_id}` | {check.result} | {check.detail} |" for check in checks
    )
    match_rows = (
        "\n".join(f"| `{hit.purl}` | `{hit.vuln_id}` | in_triage |" for hit in hits)
        or "| _(none)_ | | |"
    )
    failing = tuple(check.check_id for check in checks if check.result is CheckResult.FAIL)
    fail_line = ", ".join(failing) if failing else "none"
    return (
        "# Gatlor readiness checklist\n"
        "\n"
        f"{EXPORT_NOTICE}\n"
        "\n"
        f"Generated at (UTC): {generated_at.strftime('%Y-%m-%dT%H:%M:%SZ')}\n"
        f"SBOM sha256: `{sbom_sha256}`\n"
        f"Failing checks: {fail_line}\n"
        "\n"
        "## Checks\n"
        "\n"
        "| id | result | detail |\n"
        "| --- | --- | --- |\n"
        f"{rows}\n"
        "\n"
        "## Matches still in_triage\n"
        "\n"
        "| purl | vuln | vex |\n"
        "| --- | --- | --- |\n"
        f"{match_rows}\n"
    )
