# Licensing

Owner: Suresh Jaladanki. Design date: 6 October 2026.

How this repository is licensed. Legal rows are an operating checklist, not legal advice. Counsel reviews contracts, the DPA, and the kit licence before they are used.

This is an **open-core** product: a free OSI-open-source CLI as distribution, and a paid hosted evidence ledger as the company. Do not call the ledger "open source". FSL-1.1-ALv2 and BSL are not OSI licences.

The map in [LICENSE](../LICENSE) is the grant. This file is the why and the file-marking rules.

Copyright: Suresh Jaladanki.

## What you can do with each piece

- **Apache-2.0 (free download):** CLI, GitHub action, `ingest`, `vendors`, format-only `evidence`, evals, tests. Use, modify, redistribute, including commercially. Apache-2.0 code must never import FSL code.
- **FSL-1.1-ALv2 (paid product source):** ledger (`packages/ledger/`), API, worker, cron, review UI, `domain`, `vex`, `reporting`, `billing`, `adapters`, infra, runbooks. Read, run for your own internal use, and modify. You may not offer it as, or inside, a competing product or service. Each version turns Apache-2.0 two years after that version is published.
- **Subscription terms (not a software licence):** access to the hosted service we run. Paying does not grant source rights. Source rights come only from FSL.
- **Reserved:** indie kit templates (kit licence, when sold), unpublished operating docs, trademarks.

## 1. Split

| Part | Licence | Why |
|---|---|---|
| `apps/cli`, `.github/actions/gatlor`, and the SBOM/VEX format code the CLI needs (`packages/ingest`, `packages/vendors`, `packages/evidence`) | Apache-2.0 | Distribution channel. It wraps Syft, Grype and OSV, which are Apache-licensed. Apache adds a patent grant that MIT lacks |
| Ledger: `domain`, `ledger`, `vex`, `reporting`, `billing`, `adapters`, `api`, `review-ui`, `worker`, `cron` | FSL-1.1-ALv2 | Source-available. Anyone can read, audit and run it internally, but not run a competing commercial service. Each published version becomes Apache-2.0 after two years |
| Indie kit templates (`security.txt`, disclosure policy, Annex II text) | Proprietary, one maker per licence ([kit-licence.md](kit-licence.md)) | Sold through the merchant of record. The kit's CI action stays Apache-2.0 |
| The name "Gatlor" and logo | [TRADEMARKS.md](../TRADEMARKS.md) | A fork of the Apache CLI cannot call itself Gatlor |

Current Python packages are all on the Apache side. The ledger packages are not built yet. New paths default to FSL unless [LICENSE](../LICENSE) lists them as Apache or reserved.

**Apache packages must not import FSL packages.** Shared format types live in Apache (`ingest`, `evidence`). FSL `domain` and `ledger` may import Apache packages. Never the reverse. CI enforces this (`tests/test_licence_imports.py`).

**`packages/evidence` vs `packages/ledger`.** `evidence` is CLI format code (checklist, in-triage VEX document, claims lint) and stays Apache-2.0. SBOM store, hash binding, and technical-file export live in `packages/ledger/` under FSL. Do not add those modules to `evidence`.

`packages/ingest` is CycloneDX/SPDX parse and validate only. Ledger upload normalisation belongs with the FSL apps or `ledger`, not in Apache ingest.

## 2. Why FSL, not AGPL or closed

Buyers need to inspect the audit chain, the gates, and the "no ENISA path" test. That is hard with closed code.

FSL still blocks a competing hosted service. AGPL-3.0 plus a commercial licence is true open source and helps marketing, but deters SaaS clones less cleanly, and some companies refuse AGPL. Fully closed is simpler and gives up the trust advantage.

MIT was refused: it would let anyone host the ledger and sell it against us. Copies already shipped under MIT stay MIT; this tree has not been published, so this relicense covers the first public version.

## 3. Contributions and copyright

Copyright: Suresh Jaladanki.

Apache-path contributions require a DCO (`git commit -s`). See [CONTRIBUTING.md](../CONTRIBUTING.md) and [DCO.md](../DCO.md).

Do not accept outside FSL (ledger) contributions until a CLA exists. Open an issue instead. Without a CLA, the right to relicense beyond FSL's two-year Apache conversion is lost.

## 4. Documents that sit next to the software licence

| Document | Status | What it must say |
|---|---|---|
| Subscription terms and DPA for the ledger | Draft with counsel | Hosting in an EU region, subprocessors, deletion, clock stays with the maker, no "compliant" claims. Paying is not a source licence |
| Sprint statement of work | Draft with counsel. Include the IP clause below | Customer owns their CI configuration, SBOMs and data. Gatlor keeps tooling and pre-existing IP, and grants a licence to use any of it embedded in the deliverables |
| Indie kit licence | Draft: [kit-licence.md](kit-licence.md) | One legal entity per purchase. Templates only. CI action remains Apache-2.0 |
| Feed data terms | Software vs data split recorded 6 October 2026; per-record attribution not yet verified. Re-check before NVD ships | Advisory data is not covered by the software licence of the tool that serves it. We record the source and licence of each advisory record and attribute as its licence requires. NVD data is used under the NVD terms; this product uses the NVD API but is not endorsed or certified by the NVD. We do not attribute modified feed content to NVD. See [NOTICE](../NOTICE) |

### Sprint SOW intellectual-property clause (draft for counsel)

The Customer owns its CI configuration, SBOMs, vulnerability data, VEX decisions, report drafts, and other Customer materials produced in the engagement. Gatlor owns its pre-existing tools, playbooks, templates, and software, and any generic improvements to them. Gatlor grants the Customer a non-exclusive, perpetual licence to use any Gatlor tooling or pre-existing IP that is embedded in the sprint deliverables, solely to operate the Customer's own products. This engagement does not assign Gatlor's copyright or trademarks to the Customer.

Without this clause, a customer could argue they own the sprint playbook.

## 5. Dependencies

Avoid GPL and AGPL in the ledger. Prefer Apache-2.0, MIT, BSD, ISC, and MPL-2.0. Gatlor generates SBOMs: run the CLI on this tree in CI and keep the scan.

Direct and installed licences on 6 October 2026 (no GPL or AGPL found): Apache-2.0 (`cyclonedx-python-lib`, `py-serializable`, `license-expression`, `tzdata`, `arrow`), MIT (`pydantic`, `packageurl-python`, `jsonschema`, and others), BSD (`lxml`, `idna`, `webcolors`), ISC (`isoduration`), MPL-2.0 (`fqdn`, `pathspec`), PSF (`typing_extensions`, `defusedxml`), dual Apache-2.0 OR BSD (`packaging`). Re-scan when a ledger dependency is added.

## 6. Before this repository goes public

Copies distributed under a given licence stay under that licence. Relicense before the first public clone.

Copyright: Suresh Jaladanki. The name Gatlor is used as described in [TRADEMARKS.md](../TRADEMARKS.md). It is not a registered mark.

- [x] Replace MIT. This tree is Apache-2.0 / FSL-1.1-ALv2 / reserved, and has not been published.
- [x] Apache-path files carry SPDX identifiers. Apache packages must not import FSL packages.

## 7. How to mark a new file

- Apache path: `# SPDX-FileCopyrightText: 2026 Suresh Jaladanki` and `# SPDX-License-Identifier: Apache-2.0`
- Ledger path (`packages/ledger/` and other FSL trees): same copyright line and `# SPDX-License-Identifier: FSL-1.1-ALv2`
