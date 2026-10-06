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
