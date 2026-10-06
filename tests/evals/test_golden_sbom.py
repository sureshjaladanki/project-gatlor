# SPDX-FileCopyrightText: 2026 Suresh Jaladanki
# SPDX-License-Identifier: Apache-2.0

from gatlor_evals import golden_sbom_path
from gatlor_ingest import parse_cyclonedx_json


def test_golden_sbom_parses_components() -> None:
    parsed = parse_cyclonedx_json(golden_sbom_path().read_bytes())
    assert parsed.spec_version == "1.6"
    assert parsed.name == "fixture-app"
    names = {component.name for component in parsed.components}
    assert names == {"requests", "no-purl-lib"}
    by_name = {component.name: component for component in parsed.components}
    assert by_name["requests"].purl == "pkg:pypi/requests@2.31.0"
    assert by_name["no-purl-lib"].purl is None
