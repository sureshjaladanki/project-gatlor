# SPDX-FileCopyrightText: 2026 Suresh Jaladanki
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json

from cyclonedx.exception import MissingOptionalDependencyException
from cyclonedx.model.bom import Bom
from cyclonedx.schema import SchemaVersion
from cyclonedx.validation.json import JsonStrictValidator

from gatlor_ingest.models import ComponentRef, ParsedSbom

_SCHEMA_VERSIONS: dict[str, SchemaVersion] = {
    "1.4": SchemaVersion.V1_4,
    "1.5": SchemaVersion.V1_5,
    "1.6": SchemaVersion.V1_6,
    "1.7": SchemaVersion.V1_7,
}


class InvalidSbomError(ValueError):
    """The document is not a valid CycloneDX JSON BOM."""


def parse_cyclonedx_json(raw: bytes) -> ParsedSbom:
    text = raw.decode("utf-8")
    try:
        document = json.loads(text)
    except json.JSONDecodeError as exc:
        raise InvalidSbomError(f"SBOM is not JSON: {exc}") from exc
    if not isinstance(document, dict):
        raise InvalidSbomError("SBOM JSON must be an object")
    spec_version = str(document.get("specVersion", ""))
    schema_version = _SCHEMA_VERSIONS.get(spec_version)
    if schema_version is None:
        raise InvalidSbomError(f"Unsupported CycloneDX specVersion: {spec_version!r}")
    _validate(text, schema_version)
    bom = Bom.from_json(document)  # type: ignore[attr-defined]
    return _to_parsed(bom, spec_version)


def _validate(text: str, schema_version: SchemaVersion) -> None:
    try:
        errors = JsonStrictValidator(schema_version).validate_str(text)
    except MissingOptionalDependencyException as exc:
        raise InvalidSbomError(f"CycloneDX JSON validation extra is missing: {exc}") from exc
    if errors:
        raise InvalidSbomError(str(errors))


def _to_parsed(bom: Bom, spec_version: str) -> ParsedSbom:
    serial = str(bom.serial_number) if bom.serial_number else None
    root_name = bom.metadata.component.name if bom.metadata.component else None
    components = tuple(
        ComponentRef(
            bom_ref=str(component.bom_ref) if component.bom_ref else component.name,
            name=component.name,
            version=component.version,
            purl=str(component.purl) if component.purl else None,
            component_type=component.type.value,
        )
        for component in bom.components
    )
    return ParsedSbom(
        spec_version=spec_version,
        serial_number=serial,
        name=root_name,
        components=components,
    )
