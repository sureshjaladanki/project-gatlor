# SPDX-FileCopyrightText: 2026 Suresh Jaladanki
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from cyclonedx.model.bom import Bom
from cyclonedx.model.impact_analysis import ImpactAnalysisState
from cyclonedx.model.vulnerability import (
    BomTarget,
    Vulnerability,
    VulnerabilityAnalysis,
    VulnerabilitySource,
)
from cyclonedx.output.json import JsonV1Dot6
from pydantic import BaseModel, ConfigDict

VEX_DETAIL = (
    "Gatlor CLI does not decide whether a vulnerability affects the product. "
    "A named human at the maker must record that decision."
)


class VulnerabilityHit(BaseModel):
    model_config = ConfigDict(frozen=True)

    purl: str
    vuln_id: str
    summary: str
    aliases: tuple[str, ...] = ()


def write_in_triage_vex(
    hits: tuple[VulnerabilityHit, ...],
    *,
    product_name: str | None,
    generated_at: datetime,
) -> bytes:
    bom = Bom()
    bom.serial_number = uuid4()
    bom.metadata.timestamp = generated_at
    if product_name:
        from cyclonedx.model.component import Component, ComponentType

        bom.metadata.component = Component(name=product_name, type=ComponentType.APPLICATION)
    for hit in hits:
        aliases = ", ".join(hit.aliases)
        description = hit.summary
        if aliases:
            description = f"{description} aliases: {aliases}".strip()
        vulnerability = Vulnerability(
            id=hit.vuln_id,
            description=description or None,
            source=VulnerabilitySource(name="osv.dev"),
            analysis=VulnerabilityAnalysis(
                state=ImpactAnalysisState.IN_TRIAGE,
                detail=VEX_DETAIL,
            ),
            affects=[BomTarget(ref=hit.purl)],
        )
        bom.vulnerabilities.add(vulnerability)
    return JsonV1Dot6(bom).output_as_string(indent=2).encode("utf-8")
