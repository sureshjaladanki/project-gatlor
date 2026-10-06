# Coding conventions

Owner: Suresh Jaladanki. Design date: 5 October 2026.

How to write and review code. Layout, languages, and tooling live in [repo-conventions.md](repo-conventions.md). This file does not repeat them.

One git repository. Python under `apps/` and `packages/`. Tests under `tests/`. Do not invent extra top-level folders.

## Clean, simple, readable

Prefer clarity over cleverness. A reader should understand intent without reconstructing hidden control flow.

- Keep functions focused on one job.
- Prefer straight-line logic and small helpers over nested conditionals.
- Comment *why* when the reason is not obvious; do not narrate *what* the code already says.

## Immutable workflows — prefer functional style

Ingest, match, clock, and export are transforms: inputs in, new artifacts out. Stored evidence stays as written. Repeat a step and the result must not change beyond the first successful run.

- Prefer pure functions (`sbom in → VulnerabilityMatch[] out`, `match + product facts in → VexSuggestion out`).
- Do not mutate a caller's model, a stored Sbom, a frozen VexDecision, or a pressed ReportDraft in place.
- Pipeline steps are idempotent: key = hash of inputs, step version, and config. Re-run returns the stored output; do not append or duplicate.
- Evidence is append-only. Never repair a hash. Never fix an SBOM in place: ingest a new release.
- `recorded_at` comes from the server clock at write time. Never accept it from a client; never update it.
- Avoid hidden mutable globals; make side effects (vendor calls, alerts, refunds, exports) explicit.

## Contracts and instances — prefer objects

Release, Sbom, VulnerabilityMatch, VexDecision, ReportingClock, ReportDraft, TechnicalFileExport, ReadinessCheck, Approval, and AuditEvent are types with invariants, not loose dicts. Fields: [architectural-blueprint.md](architectural-blueprint.md) section 9.

- Python: Pydantic models. Construction fails if a required id, hash, or gate field is missing.
- Behaviour that belongs to the contract lives on the type. Ad-hoc records are for local plumbing only.
- Do not hand-maintain a parallel schema in another language. There is no TypeScript app in this repo.

## Gates, not dashboards

Evidence export and report release are invariants encoded as guards on state changes. Vocabulary: [architectural-blueprint.md](architectural-blueprint.md) sections 11–12.

- A TechnicalFileExport cannot be built unless an Sbom is bound to the same `release_hash`.
- A TechnicalFileExport cannot be built while a vulnerability match on that release has no frozen VexDecision, or while a current ReadinessCheck fails. The export is blocked, not marked incomplete.
- A ReportDraft cannot reach `pressed` without a named maker-approver Approval bound to the same `body_hash`. No code path posts to ENISA.
- A VexDecision is never deleted. A change is a new frozen decision that supersedes; both stay in the audit chain.
- Feature flags that change a gate are read on every guard call, not only on toggle.
- The engineer role has no approval, press, or export permission in prod unless that person is also wearing the operator hat, recorded as a separate action. Staff never press for a customer.

## Minimal branching

Keep control flow shallow.

- Avoid unnecessary `if` / `else` and defensive nesting.
- Do **not** add null / `None` checks “just in case.” Trust typed contracts and fail fast at the boundary when invariants break.
- Prefer early returns only when they flatten real complexity — not as a habit.

## Modular

Split by the packages in [repo-conventions.md](repo-conventions.md).

- One package ≈ one concern (`evidence`, `vex`, `reporting`).
- Public APIs accept and return the contract types above; keep helpers private with a leading `_`.
- Adapters talk to CI hosts and vendors. Domain packages do not import adapter SDKs.
- Share utilities instead of copy-pasting near-identical logic.

## DRY — don’t repeat yourself

Identical types and logic have one home.

- After a second concrete use, extract the shared type or function. One `VexDecision` for GitHub and GitLab uploads, not two lookalikes.
- Prefer one type over a class hierarchy when the shapes match. Inheritance is for genuine *is-a* behaviour, not for reusing fields.
- DRY does not override [Do not over-engineer](#do-not-over-engineer): do not invent a base class, generic, or helper for a single use.

## Do not over-engineer

Solve the problem in front of you.

- No abstractions, frameworks, or config layers until a second concrete use demands them.
- No speculative generality (“might need later”).
- Prefer the simplest correct implementation that matches existing patterns in the repo.
- Do not add a message broker, SPA, or warehouse because the design mentioned scale later.

## Clear nomenclature

Names encode role and meaning. Use the vocabulary in [architectural-blueprint.md](architectural-blueprint.md) (release, SBOM, VEX, clock, press, kept revenue) — not parallel synonyms (do not rename a VEX a “ticket” in code).

Follow Python in Python files. Templates stay HTML.

### Python (`apps/`, `packages/`, `tests/`)

| Kind | Convention | Examples |
|------|------------|----------|
| Modules / files | `snake_case` | `state_machine.py`, `readiness.py` |
| Functions | verb + object, `snake_case` | `match_release`, `assemble_export` |
| Variables | `snake_case`, domain terms | `product_line_id`, `release_hash`, `vex_decision_id` |
| Constants | `SCREAMING_SNAKE_CASE` | `EARLY_WARNING_HOURS`, `REFUND_SLA_HOURS` |
| Classes / models | `PascalCase` | `Release`, `VexDecision`, `ReportDraft` |
| Private helpers | leading `_` | `_idempotency_key`, `_claims_lint` |
| Table / column names | stable `snake_case` | `release_hash`, `kept_cents`, `recorded_at` |

Never use desk-system names (`open_move`, `sku`, `demand_note`, `persona`) in this repo.

### Data files (`apps/cli/`, `packages/evals/`)

Checklist text, report templates, and golden fixtures are data, not code. Keep them versioned and passing the claims lint. A merge makes a fixture available; it does not change a production gate.

## Respect repository conventions

Paths, languages, package managers, linters, and forbidden stacks: [repo-conventions.md](repo-conventions.md).

Match the surrounding code before introducing a new style.

- Python lives in `apps/` and `packages/`. Tests live in `tests/`.
- New Python files start with SPDX copyright and licence identifiers that match [licensing.md](licensing.md).
- Prefer libraries already named in repo conventions (FastAPI, Pydantic, pytest, ruff, mypy). Do not add a second schema stack.
- When editing a file, mirror its naming, import style, and structure rather than reformatting unrelated code.
- New docs under `docs/` use kebab-case filenames.

When in doubt: **read a nearby module and do the same thing, only simpler.**
