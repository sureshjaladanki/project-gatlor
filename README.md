# Gatlor

CRA engineering for small makers: a free CLI, a build-in sprint, and a subscription evidence ledger.

The CLI wraps [Syft](https://github.com/anchore/syft) and [OSV](https://osv.dev). It writes a CycloneDX SBOM, a CycloneDX VEX file with every match left `in_triage`, and a readiness checklist. A named human at the maker records each VEX decision. Gatlor does not file reports and does not say that a product meets the Cyber Resilience Act.

## CLI

Python 3.12 and [uv](https://docs.astral.sh/uv/). Syft must be on `PATH` unless you pass an existing SBOM.

```text
uv sync
uv run gatlor scan --path . --out-dir dist/gatlor --repo-root .
```

`--repo-root` is the directory that holds `SECURITY.md` and `SUPPORT.md`.

Outputs:

- `dist/gatlor/sbom.cdx.json` — Syft CycloneDX JSON, stored as generated
- `dist/gatlor/vex.cdx.json` — OSV matches, analysis state `in_triage`
- `dist/gatlor/readiness-checklist.md` — evidence gaps for this tree

Use an existing SBOM (no Syft):

```text
uv run gatlor scan --sbom path/to/sbom.cdx.json --out-dir dist/gatlor --repo-root .
```

## CI action

This repository's workflow runs the CLI after lint and tests. Other repos can call the composite action at `.github/actions/gatlor` after checking out this tree (or, later, an installed package).

## Gatlor's own product files

- [SECURITY.md](SECURITY.md) — disclosure policy
- [SUPPORT.md](SUPPORT.md) — support period (`support_period_end: 2028-04-05`)

## Checks

```text
uv run ruff check .
uv run ruff format --check .
uv run mypy --strict packages/evidence
uv run pytest
```

## License

Open-core. The CLI, the CI action, and the SBOM/VEX format code they need are [Apache-2.0](LICENSE-APACHE) (OSI open source). The hosted evidence ledger, when added, is [FSL-1.1-ALv2](LICENSE-FSL): source-available, not OSI open source. Each ledger version becomes Apache-2.0 two years after it is published. The name Gatlor is a [trademark](TRADEMARKS.md).

See [LICENSE](LICENSE), [docs/licensing.md](docs/licensing.md), and [CONTRIBUTING.md](CONTRIBUTING.md).
