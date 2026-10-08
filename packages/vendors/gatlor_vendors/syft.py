# SPDX-FileCopyrightText: 2026 Suresh Jaladanki
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import subprocess
from pathlib import Path


class SyftNotFoundError(RuntimeError):
    """Syft is not installed or not on PATH."""


DECLARED_CATALOGERS = "declared"


def generate_cyclonedx(scan_path: Path, *, executable: str = "syft") -> bytes:
    try:
        proc = subprocess.run(
            [
                executable,
                "scan",
                str(scan_path),
                "--select-catalogers",
                DECLARED_CATALOGERS,
                "-o",
                "cyclonedx-json",
            ],
            check=False,
            capture_output=True,
        )
    except FileNotFoundError as exc:
        raise SyftNotFoundError(
            "Syft was not found on PATH. Install https://github.com/anchore/syft and retry."
        ) from exc
    if proc.returncode != 0:
        detail = proc.stderr.decode("utf-8", errors="replace").strip() or "unknown Syft error"
        raise RuntimeError(f"Syft failed (exit {proc.returncode}): {detail}")
    if not proc.stdout:
        raise RuntimeError("Syft wrote an empty CycloneDX document")
    return proc.stdout
