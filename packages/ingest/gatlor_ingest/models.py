# SPDX-FileCopyrightText: 2026 Suresh Jaladanki
# SPDX-License-Identifier: Apache-2.0

from pydantic import BaseModel, ConfigDict


class ComponentRef(BaseModel):
    model_config = ConfigDict(frozen=True)

    bom_ref: str
    name: str
    version: str | None
    purl: str | None
    component_type: str = "library"

    def needs_purl(self) -> bool:
        if self.component_type == "file":
            return False
        normalized = self.name.replace("\\", "/")
        return not (normalized.startswith(".") or normalized.startswith("/"))


class ParsedSbom(BaseModel):
    model_config = ConfigDict(frozen=True)

    spec_version: str
    serial_number: str | None
    name: str | None
    components: tuple[ComponentRef, ...]
