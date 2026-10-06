# SPDX-FileCopyrightText: 2026 Suresh Jaladanki
# SPDX-License-Identifier: Apache-2.0

"""Apache-2.0 trees must not import FSL modules."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

APACHE_TREES = (
    ROOT / "apps" / "cli",
    ROOT / "packages" / "ingest",
    ROOT / "packages" / "vendors",
    ROOT / "packages" / "evidence",
    ROOT / "packages" / "evals",
    ROOT / "tests",
)

FSL_TREES = (
    ROOT / "apps" / "api",
    ROOT / "apps" / "review-ui",
    ROOT / "apps" / "worker",
    ROOT / "apps" / "cron",
    ROOT / "packages" / "domain",
    ROOT / "packages" / "ledger",
    ROOT / "packages" / "vex",
    ROOT / "packages" / "reporting",
    ROOT / "packages" / "billing",
    ROOT / "packages" / "adapters",
)

APACHE_SPDX = "SPDX-License-Identifier: Apache-2.0"
FSL_SPDX = "SPDX-License-Identifier: FSL-1.1-ALv2"

FSL_MODULES = {
    "gatlor_domain",
    "gatlor_ledger",
    "gatlor_vex",
    "gatlor_reporting",
    "gatlor_billing",
    "gatlor_adapters",
    "gatlor_api",
    "gatlor_worker",
    "gatlor_cron",
}

FSL_WORKSPACE = {
    "gatlor-domain",
    "gatlor-ledger",
    "gatlor-vex",
    "gatlor-reporting",
    "gatlor-billing",
    "gatlor-adapters",
}


def _imported_roots(tree: ast.AST) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name.split(".", 1)[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".", 1)[0])
    return names


def test_apache_python_does_not_import_fsl_modules() -> None:
    offenders: list[str] = []
    for tree_root in APACHE_TREES:
        for path in tree_root.rglob("*.py"):
            parsed = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            hits = _imported_roots(parsed) & FSL_MODULES
            if hits:
                rel = path.relative_to(ROOT).as_posix()
                offenders.append(f"{rel}: {', '.join(sorted(hits))}")
    assert not offenders, "Apache paths imported FSL modules:\n" + "\n".join(offenders)


def test_apache_python_has_apache_spdx() -> None:
    missing: list[str] = []
    for tree_root in APACHE_TREES:
        if not tree_root.is_dir():
            continue
        for path in tree_root.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            if APACHE_SPDX not in text:
                missing.append(path.relative_to(ROOT).as_posix())
    assert not missing, "Apache Python files missing Apache SPDX:\n" + "\n".join(missing)


def test_fsl_python_has_fsl_spdx() -> None:
    missing: list[str] = []
    for tree_root in FSL_TREES:
        if not tree_root.is_dir():
            continue
        for path in tree_root.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            if FSL_SPDX not in text:
                missing.append(path.relative_to(ROOT).as_posix())
    assert not missing, "FSL Python files missing FSL SPDX:\n" + "\n".join(missing)


def test_apache_pyproject_does_not_depend_on_fsl_packages() -> None:
    offenders: list[str] = []
    for tree_root in APACHE_TREES:
        pyproject = tree_root / "pyproject.toml"
        if not pyproject.is_file():
            continue
        text = pyproject.read_text(encoding="utf-8")
        for name in FSL_WORKSPACE:
            if name in text:
                rel = pyproject.relative_to(ROOT).as_posix()
                offenders.append(f"{rel}: {name}")
    assert not offenders, "Apache pyproject depends on FSL packages:\n" + "\n".join(offenders)
