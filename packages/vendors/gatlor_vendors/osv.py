# SPDX-FileCopyrightText: 2026 Suresh Jaladanki
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
from collections.abc import Callable, Sequence
from typing import Any
from urllib.request import Request, urlopen

from packageurl import PackageURL
from pydantic import BaseModel, ConfigDict

OSV_DEFAULT_BASE_URL = "https://api.osv.dev"

UrlOpen = Callable[..., Any]


class OsvQuery(BaseModel):
    model_config = ConfigDict(frozen=True)

    purl: str

    def to_payload(self) -> dict[str, object]:
        package_purl, version = _split_purl(self.purl)
        payload: dict[str, object] = {"package": {"purl": package_purl}}
        if version:
            payload["version"] = version
        return payload


class OsvHit(BaseModel):
    model_config = ConfigDict(frozen=True)

    purl: str
    vuln_id: str
    summary: str
    aliases: tuple[str, ...]


class OsvClient:
    def __init__(
        self,
        *,
        base_url: str = OSV_DEFAULT_BASE_URL,
        opener: UrlOpen = urlopen,
        timeout_seconds: float = 30.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._opener = opener
        self._timeout_seconds = timeout_seconds

    def query_batch(self, queries: Sequence[OsvQuery]) -> tuple[OsvHit, ...]:
        if not queries:
            return ()
        body = json.dumps({"queries": [query.to_payload() for query in queries]}).encode()
        request = Request(
            f"{self._base_url}/v1/querybatch",
            data=body,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "gatlor-cli/0.1",
            },
            method="POST",
        )
        with self._opener(request, timeout=self._timeout_seconds) as response:
            payload = json.load(response)
        return _hits_from_batch(queries, payload)


def _split_purl(purl: str) -> tuple[str, str | None]:
    parsed = PackageURL.from_string(purl)
    version = parsed.version
    without_version = PackageURL(
        type=parsed.type,
        namespace=parsed.namespace,
        name=parsed.name,
        qualifiers=parsed.qualifiers,
        subpath=parsed.subpath,
    )
    return str(without_version), version


def _hits_from_batch(queries: Sequence[OsvQuery], payload: object) -> tuple[OsvHit, ...]:
    if not isinstance(payload, dict):
        raise ValueError("OSV querybatch response must be an object")
    results = payload.get("results")
    if not isinstance(results, list) or len(results) != len(queries):
        raise ValueError("OSV querybatch results length must match queries")
    hits: list[OsvHit] = []
    for query, result in zip(queries, results, strict=True):
        if not isinstance(result, dict):
            raise ValueError("OSV querybatch result must be an object")
        vulns = result.get("vulns") or []
        if not isinstance(vulns, list):
            raise ValueError("OSV vulns must be a list")
        for vuln in vulns:
            if not isinstance(vuln, dict):
                raise ValueError("OSV vuln must be an object")
            vuln_id = str(vuln.get("id") or "")
            if not vuln_id:
                raise ValueError("OSV vuln is missing id")
            aliases_raw = vuln.get("aliases") or []
            if not isinstance(aliases_raw, list):
                raise ValueError("OSV aliases must be a list")
            hits.append(
                OsvHit(
                    purl=query.purl,
                    vuln_id=vuln_id,
                    summary=str(vuln.get("summary") or ""),
                    aliases=tuple(str(alias) for alias in aliases_raw),
                )
            )
    return tuple(hits)
