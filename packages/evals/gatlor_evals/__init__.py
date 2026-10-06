# SPDX-FileCopyrightText: 2026 Suresh Jaladanki
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"


def golden_sbom_path() -> Path:
    return FIXTURES / "golden_sbom.cdx.json"
