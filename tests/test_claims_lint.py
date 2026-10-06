# SPDX-FileCopyrightText: 2026 Suresh Jaladanki
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

from gatlor_evidence.claims import lint_text

_COPY_FILES = (
    Path("README.md"),
    Path("SECURITY.md"),
    Path("SUPPORT.md"),
)


def test_published_copy_passes_claims_lint() -> None:
    for path in _COPY_FILES:
        hits = lint_text(path.read_text(encoding="utf-8"))
        assert hits == (), f"{path} has claim language: {hits}"
