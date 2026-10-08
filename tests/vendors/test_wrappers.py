# SPDX-FileCopyrightText: 2026 Suresh Jaladanki
# SPDX-License-Identifier: Apache-2.0

from io import BytesIO
from pathlib import Path
from unittest.mock import patch

import pytest

from gatlor_vendors.osv import OsvClient, OsvQuery
from gatlor_vendors.syft import SyftNotFoundError, generate_cyclonedx


def test_osv_query_batch_maps_hits() -> None:
    def opener(request: object, timeout: object = None) -> BytesIO:
        del request, timeout
        return BytesIO(
            b'{"results":[{"vulns":[{"id":"GHSA-1","summary":"one","aliases":["CVE-1"]}]}]}'
        )

    client = OsvClient(opener=opener)
    hits = client.query_batch([OsvQuery(purl="pkg:pypi/requests@2.31.0")])
    assert len(hits) == 1
    assert hits[0].vuln_id == "GHSA-1"
    assert hits[0].purl == "pkg:pypi/requests@2.31.0"
    assert hits[0].aliases == ("CVE-1",)


def test_osv_query_payload_splits_purl_version() -> None:
    payload = OsvQuery(purl="pkg:pypi/requests@2.31.0").to_payload()
    assert payload == {"package": {"purl": "pkg:pypi/requests"}, "version": "2.31.0"}


def test_syft_missing_binary() -> None:
    with pytest.raises(SyftNotFoundError):
        generate_cyclonedx(Path("."), executable="syft-not-installed-for-tests")


def test_syft_nonzero_exit() -> None:
    with patch("gatlor_vendors.syft.subprocess.run") as run:
        run.return_value.returncode = 2
        run.return_value.stderr = b"boom"
        run.return_value.stdout = b""
        with pytest.raises(RuntimeError, match="Syft failed"):
            generate_cyclonedx(Path("."))


def test_syft_selects_declared_catalogers() -> None:
    with patch("gatlor_vendors.syft.subprocess.run") as run:
        run.return_value.returncode = 0
        run.return_value.stderr = b""
        run.return_value.stdout = b'{"bomFormat":"CycloneDX"}'
        generate_cyclonedx(Path("."))
        args = run.call_args[0][0]
        assert "--select-catalogers" in args
        assert args[args.index("--select-catalogers") + 1] == "declared"
        assert "--exclude" not in args
