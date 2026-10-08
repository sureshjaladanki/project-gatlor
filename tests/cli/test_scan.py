# SPDX-FileCopyrightText: 2026 Suresh Jaladanki
# SPDX-License-Identifier: Apache-2.0

from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path

from gatlor_cli.scan import run_scan
from gatlor_evals import golden_sbom_path
from gatlor_vendors.osv import OsvClient


def test_scan_writes_three_artifacts(tmp_path: Path) -> None:
    (tmp_path / "SECURITY.md").write_text(
        "Report security issues via GitHub private advisories.\n", encoding="utf-8"
    )
    (tmp_path / "SUPPORT.md").write_text("support_period_end: 2028-04-05\n", encoding="utf-8")
    sbom = tmp_path / "in.cdx.json"
    raw = golden_sbom_path().read_bytes()
    sbom.write_bytes(raw)
    out = tmp_path / "out"

    def fail_syft(_path: Path) -> bytes:
        raise AssertionError("Syft must not run when --sbom is set")

    def opener(request: object, timeout: object = None) -> BytesIO:
        del request, timeout
        body = (
            b'{"results":[{"vulns":[{"id":"GHSA-fixture",'
            b'"summary":"fixture match","aliases":["CVE-0000-0000"]}]}]}'
        )
        return BytesIO(body)

    written = run_scan(
        scan_path=tmp_path,
        out_dir=out,
        repo_root=tmp_path,
        osv_client=OsvClient(opener=opener),
        syft=fail_syft,
        sbom_path=sbom,
        clock=lambda: datetime(2026, 10, 5, tzinfo=UTC),
    )
    assert written["sbom"].read_bytes() == raw
    vex = written["vex"].read_text(encoding="utf-8")
    assert "in_triage" in vex
    assert "GHSA-fixture" in vex
    checklist = written["checklist"].read_text(encoding="utf-8")
    assert "vex-decided" in checklist
    assert "fail" in checklist


def test_scan_ignores_files_and_local_actions_for_purl(tmp_path: Path) -> None:
    (tmp_path / "SECURITY.md").write_text(
        "Report security issues via GitHub private advisories.\n", encoding="utf-8"
    )
    (tmp_path / "SUPPORT.md").write_text("support_period_end: 2028-04-05\n", encoding="utf-8")
    sbom = tmp_path / "in.cdx.json"
    sbom.write_text(
        """{
          "bomFormat": "CycloneDX",
          "specVersion": "1.6",
          "version": 1,
          "metadata": {"component": {"type": "application", "name": "fixture-app"}},
          "components": [
            {"type": "file", "name": "ci.yml", "bom-ref": "file-ci"},
            {
              "type": "library",
              "name": "./.github/actions/gatlor",
              "version": "UNKNOWN",
              "bom-ref": "local-action"
            },
            {
              "type": "library",
              "name": "attrs",
              "version": "26.1.0",
              "purl": "pkg:pypi/attrs@26.1.0",
              "bom-ref": "pkg:pypi/attrs@26.1.0"
            }
          ]
        }""",
        encoding="utf-8",
    )

    def fail_syft(_path: Path) -> bytes:
        raise AssertionError("Syft must not run when --sbom is set")

    def opener(request: object, timeout: object = None) -> BytesIO:
        del request, timeout
        return BytesIO(b'{"results":[{}]}')

    written = run_scan(
        scan_path=tmp_path,
        out_dir=tmp_path / "out",
        repo_root=tmp_path,
        osv_client=OsvClient(opener=opener),
        syft=fail_syft,
        sbom_path=sbom,
        clock=lambda: datetime(2026, 10, 5, tzinfo=UTC),
    )
    checklist = written["checklist"].read_text(encoding="utf-8")
    assert "| `component-purl` | pass |" in checklist
    assert "every component has a purl" in checklist
