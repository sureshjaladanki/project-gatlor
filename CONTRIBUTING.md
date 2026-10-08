# Contributing

Copyright: Suresh Jaladanki.

## Licences

This is an open-core repository. The map is in [LICENSE](LICENSE) and [docs/licensing.md](docs/licensing.md).

- Apache-2.0 paths (CLI, CI action, ingest, vendors, and today's evidence format code) are OSI open source.
- FSL-1.1-ALv2 paths (the hosted ledger, when added) are source-available. Do not call them open source.
- Put SBOM store, hash binding, and technical-file export in `packages/ledger/` (FSL). Do not add them to an Apache-2.0 package. Apache packages must not import FSL packages.

We do not accept outside contributions to FSL paths until a CLA is in place. Open an issue instead. The CLA will be a copyright licence (or assignment) to the copyright holder, with a patent grant, drafted by counsel.

## DCO (Apache-2.0 paths only)

Every commit that touches Apache-2.0 files must include:

```text
Signed-off-by: Your Name <you@example.com>
```

`git commit -s` adds it. That sign-off is your agreement to [DCO.md](DCO.md). For Apache-2.0 files, DCO clause (a) applies as written: you submit under Apache-2.0.

Do not use the DCO as the grant for FSL files.

## Branching

Do not commit to `main`. Open a feature branch and land changes with a **squash merge** pull request. GitHub enforces this: direct pushes, merge commits, rebase merges, and force-pushes to `main` are blocked. A second review is not required.

## Code

Follow [docs/coding-conventions.md](docs/coding-conventions.md) and [docs/repo-conventions.md](docs/repo-conventions.md). New Python files carry SPDX headers matching their directory's licence.
