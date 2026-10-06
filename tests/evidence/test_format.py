# SPDX-FileCopyrightText: 2026 Suresh Jaladanki
# SPDX-License-Identifier: Apache-2.0

from datetime import UTC, datetime
from pathlib import Path

from gatlor_evidence.checklist import CheckResult, render_checklist, run_checks
from gatlor_evidence.claims import lint_text
from gatlor_evidence.vex import VulnerabilityHit, write_in_triage_vex


def test_lint_finds_forbidden_terms() -> None:
    hits = lint_text("This product is compliant and CRA-ready with a guarantee.")
    terms = {hit.term.lower() for hit in hits}
    assert "compliant" in terms
    assert "cra-ready" in terms
    assert any(term.startswith("guarantee") for term in terms)


def test_in_triage_vex_marks_matches() -> None:
    hits = (VulnerabilityHit(purl="pkg:pypi/requests@2.31.0", vuln_id="GHSA-1", summary="one"),)
    raw = write_in_triage_vex(
        hits, product_name="fixture-app", generated_at=datetime(2026, 10, 5, tzinfo=UTC)
    )
    text = raw.decode("utf-8")
    assert "in_triage" in text
    assert "GHSA-1" in text
    assert "does not decide" in text


def test_checklist_fails_undecided_vex_and_missing_purl(tmp_path: Path) -> None:
    (tmp_path / "SECURITY.md").write_text(
        "Report issues via GitHub private advisories.\n", encoding="utf-8"
    )
    (tmp_path / "SUPPORT.md").write_text("support_period_end: 2028-04-05\n", encoding="utf-8")
    hits = (VulnerabilityHit(purl="pkg:pypi/requests@2.31.0", vuln_id="GHSA-1", summary="one"),)
    checks = run_checks(
        spec_version="1.6",
        component_count=2,
        missing_purl_count=1,
        queried_purl_count=1,
        hits=hits,
        repo_root=tmp_path,
    )
    by_id = {check.check_id: check for check in checks}
    assert by_id["vex-decided"].result is CheckResult.FAIL
    assert by_id["component-purl"].result is CheckResult.FAIL
    assert by_id["disclosure-policy"].result is CheckResult.PASS
    assert by_id["support-period"].result is CheckResult.PASS
    markdown = render_checklist(
        checks,
        hits,
        generated_at=datetime(2026, 10, 5, tzinfo=UTC),
        sbom_sha256="abc",
    )
    assert "not a statement that the product meets the Cyber Resilience Act" in markdown
    assert "GHSA-1" in markdown
