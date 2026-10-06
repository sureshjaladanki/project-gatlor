# SPDX-FileCopyrightText: 2026 Suresh Jaladanki
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import re

from pydantic import BaseModel, ConfigDict

_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bcompliant\b", re.IGNORECASE),
    re.compile(r"\bcertified\b", re.IGNORECASE),
    re.compile(r"cra-ready", re.IGNORECASE),
    re.compile(r"\bguarantee", re.IGNORECASE),
)


class ClaimsLintHit(BaseModel):
    model_config = ConfigDict(frozen=True)

    term: str
    line_number: int
    line: str


def lint_text(text: str) -> tuple[ClaimsLintHit, ...]:
    hits: list[ClaimsLintHit] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for pattern in _PATTERNS:
            match = pattern.search(line)
            if match:
                hits.append(
                    ClaimsLintHit(term=match.group(0), line_number=line_number, line=line.strip())
                )
    return tuple(hits)
