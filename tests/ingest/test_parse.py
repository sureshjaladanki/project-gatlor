# SPDX-FileCopyrightText: 2026 Suresh Jaladanki
# SPDX-License-Identifier: Apache-2.0

import json

import pytest

from gatlor_ingest import InvalidSbomError, parse_cyclonedx_json


def test_invalid_json_is_rejected() -> None:
    with pytest.raises(InvalidSbomError):
        parse_cyclonedx_json(b"not-json")


def test_missing_spec_version_is_rejected() -> None:
    with pytest.raises(InvalidSbomError):
        parse_cyclonedx_json(json.dumps({"bomFormat": "CycloneDX"}).encode())


def _minimal_bom(*components: dict[str, object]) -> bytes:
    return json.dumps(
        {
            "bomFormat": "CycloneDX",
            "specVersion": "1.6",
            "version": 1,
            "components": list(components),
        }
    ).encode()


def test_file_and_local_path_components_do_not_need_purl() -> None:
    parsed = parse_cyclonedx_json(
        _minimal_bom(
            {"type": "file", "name": "ci.yml", "bom-ref": "file-ci"},
            {
                "type": "library",
                "name": "./.github/actions/gatlor",
                "version": "UNKNOWN",
                "bom-ref": "local-action",
            },
            {
                "type": "library",
                "name": "attrs",
                "version": "26.1.0",
                "bom-ref": "attrs",
            },
        )
    )
    by_name = {component.name: component for component in parsed.components}
    assert by_name["ci.yml"].component_type == "file"
    assert by_name["ci.yml"].needs_purl() is False
    assert by_name["./.github/actions/gatlor"].needs_purl() is False
    assert by_name["attrs"].needs_purl() is True
