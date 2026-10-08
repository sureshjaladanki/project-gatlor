# Repo conventions

Owner: Suresh Jaladanki. Design date: 5 October 2026.

Layout, tooling and what is forbidden in this repo. How to write code is [coding-conventions.md](coding-conventions.md). The product contract (what Gatlor does, its gates and data model) is [architectural-blueprint.md](architectural-blueprint.md). This file does not repeat it. Cursor rules in `.cursor/rules/` point at these docs.

## Product

One repo, one product: **Gatlor**, CRA engineering for small makers. That means a free CLI, build-in sprints, and the subscription evidence ledger.

The evidence ledger is a modular monolith: one codebase, one Postgres database, one object store, one container image run as `api`, `worker`, and `cron`. It does not take payment, host a storefront, or run a marketplace. Kit and subscriptions go through a merchant of record (Paddle or Lemon Squeezy, one chosen on first use). Sprints, reviews, and retainers are invoiced directly.

## Layout

| Path | Licence | Owns |
|---|---|---|
| `apps/api` | FSL-1.1-ALv2 | FastAPI: auth, CI upload, billing webhooks |
| `apps/review-ui` | FSL-1.1-ALv2 | Server-rendered HTML + HTMX |
| `apps/worker` | FSL-1.1-ALv2 | Ingest, match, checks, clock, drafts, export jobs |
| `apps/cron` | FSL-1.1-ALv2 | Daily feed sync and re-match, clock ticks, chain verify, records export |
| `apps/cli` | Apache-2.0 | Free CLI + CI action |
| `packages/domain` | FSL-1.1-ALv2 | Entities, state machines, guards, `transition()`, audit event |
| `packages/evidence` | Apache-2.0 | CLI format only: checklist, in-triage VEX document, claims lint |
| `packages/ledger` | FSL-1.1-ALv2 | SBOM store, hash binding, readiness checks, technical-file export |
| `packages/vex` | FSL-1.1-ALv2 | Decisions, reason codes, supersede-not-delete, suggestions |
| `packages/reporting` | FSL-1.1-ALv2 | Clock, 24h, 72h and 14-day drafts, human press |
| `packages/ingest` | Apache-2.0 | CycloneDX/SPDX parse and validate |
| `packages/adapters` | FSL-1.1-ALv2 | GitHub, GitLab, generic CI |
| `packages/vendors` | Apache-2.0 | OSV, NVD, scanner wrappers |
| `packages/billing` | FSL-1.1-ALv2 | MoR webhooks, invoice records (no card capture) |
| `packages/evals` | Apache-2.0 | Golden SBOM and VEX fixtures for Apache packages |
| `infra/` | FSL-1.1-ALv2 | OpenTofu only |
| `runbooks/` | FSL-1.1-ALv2 | One file per alert |
| `docs/` | FSL-1.1-ALv2 unless listed Apache in LICENSE | kebab-case markdown |
| `tests/` | Apache-2.0 until an FSL test tree is added | pytest; mirror package names |

Do not add `src/`, a second app tree, a frontend SPA, or a data-warehouse project. Do not invent extra top-level folders. `packages/evidence` is format code. Do not put the ledger store there.

## Languages and packaging

| Area | Language | Package manager |
|------|----------|-----------------|
| Apps and packages | Python 3.12 | `uv` workspaces |
| Review UI templates | HTML + HTMX (no separate JS app) | same workspace |
| Infra | OpenTofu | `infra/` |
| CLI checklist and golden fixtures | markdown, YAML, recorded files | `apps/cli/`, `packages/evals/` |

- One `pyproject.toml` at the repo root. Workspace members are `apps/*` and `packages/*`.
- Pin Python to 3.12. Do not add a second runtime (Node, Go, a second Python major) unless [architectural-blueprint.md](architectural-blueprint.md) is updated in the same change.
- Database: Postgres 16. Local object store: MinIO (S3-compatible). No Redis, no extra message broker: the job queue is a Postgres `SKIP LOCKED` table.

## Libraries that are in

Prefer these before adding a new dependency:

| Job | Library |
|-----|---------|
| HTTP API | FastAPI |
| Domain models | Pydantic |
| Database | SQLAlchemy or psycopg, one choice for the repo; pick it on first use and keep it |
| Tests | pytest |
| Lint / format | ruff |
| Types | mypy (`--strict` on `domain`, `ledger`, `vex`, `reporting`) |
| Traces | OpenTelemetry |
| Infra | OpenTofu |
| SBOM formats | Official CycloneDX and SPDX libraries; no hand-rolled parsers |
| Scanners and feeds | Existing tools (Syft, Grype and similar) and OSV/NVD, called from `vendors/` or the CLI. Never rewritten |

Do not add a second schema stack, a second web framework, or an ORM alongside the first one.

## Commands

Until the repo is bootstrapped, treat these as the intended interface:

```text
uv sync
uv run ruff check .
uv run ruff format --check .
uv run mypy --strict packages/evidence
uv run pytest
```

When FSL packages exist, also `mypy --strict` on `packages/domain`, `packages/ledger`, `packages/vex`, `packages/reporting`.

Evals run when `packages/evidence`, `packages/ledger`, `packages/vex`, `packages/ingest`, `packages/vendors`, or `packages/evals` change:

```text
uv run pytest tests/evals
```

## Environments

| Env | Data | Scanners / feeds | CI | Billing |
|-----|------|------------------|----|---------|
| local | Docker Postgres, MinIO | Fakes and recorded fixtures | Fake adapters | Fake webhooks |
| staging | Synthetic records | Real feeds, low caps | Canary / test repos | MoR test mode; test product |
| prod | Real | Real, EU region | Customer CI | Live MoR + invoicing |

Secrets live in the cloud secret manager, injected at runtime. Never commit tokens, `.env` with live credentials, or platform cookies. Infra changes go through `infra/`. Customer data is hosted in an EU region from day 1.

## Licensing

Open-core. Map: [LICENSE](../LICENSE). Detail: [licensing.md](licensing.md).

| Path | Licence |
|---|---|
| `apps/cli`, `.github/actions/gatlor`, `packages/ingest`, `packages/vendors`, `packages/evidence` (format only), `packages/evals` | Apache-2.0 |
| Ledger apps and packages (`api`, `review-ui`, `worker`, `cron`, `domain`, `ledger`, `vex`, `reporting`, `billing`, `adapters`, `infra/`) | FSL-1.1-ALv2. Not OSI open source |
| Kit templates | Proprietary, one maker per licence |
| Name "Gatlor" and logo | [TRADEMARKS.md](../TRADEMARKS.md) |

New Python files carry SPDX identifiers for their directory. Put store, hash binding, and technical-file export in `packages/ledger/`. Apache packages must not import FSL packages. Do not add GPL or AGPL dependencies. Contributions: [CONTRIBUTING.md](../CONTRIBUTING.md).

## Forbidden in this repo

- Taking payment or building checkout, headless commerce, or a custom storefront. Gumroad and Whop are not used.
- A marketplace or a consumer subscription app.
- A data warehouse or a second analytics database.
- Any code path that files, submits, or posts to ENISA. A named human at the maker files.
- Backdating evidence, or setting `recorded_at` from client input.
- Deleting a VEX decision. Supersede only.
- Hiding, muting, or suppressing a vulnerability match.
- "Compliant", "certified", or "CRA-ready guaranteed" in product copy, templates, exports, or emails.
- Legal opinions or notified-body work in product copy.
- 24/7 SOC or on-call cover staffed by Gatlor.
- In-house binary firmware analysis, or rewrites of existing scanners.
- A GRC platform, ISO 27001 or NIS2 crosswalk.
- Enabling a gate-changing feature flag that is checked only on toggle, not on every guard read.
- A publish or export path without a named human press, or a press that covers more than one subject.
- Console-only infrastructure. Infra changes go through `infra/`.
- Secrets in the repo.

## Docs and runbooks

- Product and process docs: `docs/`, kebab-case (`architectural-blueprint.md`).
- Core docs: `vision.md`, `architectural-blueprint.md`, `repo-conventions.md`, `coding-conventions.md`, `agent-guidelines.md`, `licensing.md`.
- Operating cadence, pricing, and stop-rules are unpublished. Do not put them in the public `docs/` tree.
- Do not commit to `main`. Land on `main` only by squash-merging a pull request from a feature branch. See [CONTRIBUTING.md](../CONTRIBUTING.md).
- A change to a gate, entity, or state machine updates [architectural-blueprint.md](architectural-blueprint.md) in the same pull request.
- Incident runbooks: `runbooks/`, one file per runbook. Expected files: `missed-clock.md`, `broken-audit-chain.md`, `eu-hosting.md`, `feed-outage.md`, `suppress-request.md`, `claims-language.md`, `backup-read.md`.
- Cursor rules in `.cursor/rules/` point at these docs. Do not duplicate the full text in the rule file.
