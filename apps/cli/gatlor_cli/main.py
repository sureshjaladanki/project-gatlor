# SPDX-FileCopyrightText: 2026 Suresh Jaladanki
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable, Sequence
from pathlib import Path

from gatlor_cli.scan import ScanError, run_scan
from gatlor_vendors.osv import OsvClient
from gatlor_vendors.syft import generate_cyclonedx


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="gatlor",
        description=(
            "Wrap Syft and OSV. Write a CycloneDX SBOM, a VEX file with matches in_triage, "
            "and a readiness checklist. The CLI does not decide VEX and does not file reports."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)
    scan = sub.add_parser("scan", help="Generate SBOM, match OSV, write VEX and checklist")
    scan.add_argument("--path", type=Path, default=Path("."), help="Tree for Syft to scan")
    scan.add_argument("--out-dir", type=Path, default=Path("dist/gatlor"))
    scan.add_argument(
        "--repo-root", type=Path, default=None, help="Where SECURITY.md and SUPPORT.md live"
    )
    scan.add_argument(
        "--sbom",
        type=Path,
        default=None,
        help="Use this CycloneDX JSON instead of running Syft",
    )
    scan.add_argument("--osv-url", default="https://api.osv.dev")
    args = parser.parse_args(argv)
    if args.command != "scan":
        parser.error("unknown command")
    syft: Callable[[Path], bytes] = generate_cyclonedx
    try:
        run_scan(
            scan_path=args.path,
            out_dir=args.out_dir,
            repo_root=args.repo_root or args.path,
            sbom_path=args.sbom,
            osv_client=OsvClient(base_url=args.osv_url),
            syft=syft,
        )
    except ScanError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0
