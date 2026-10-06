# Agent guidelines

How agents talk in this repo. Code style is in [coding-conventions.md](coding-conventions.md). Tooling is in [repo-conventions.md](repo-conventions.md).

## All models: readable replies

Write for a person who wants the answer, not a report.

- Use plain English. Prefer everyday words over domain jargon. If a term is required (sleeve, hurdle, MDE), define it once, then use it.
- Keep replies short. Say the outcome, then only the detail needed to act on it.
- Completeness still matters: include the decision, the files touched, and the next step. Cut the diary of how you got there.
- Do not recap the whole task, narrate tool calls, or write journal-style sections the user did not ask for.

```text
# ❌ BAD
I started by exploring the repository structure, then I reviewed the relevant
modules, after which I implemented a carefully considered change to the cost
path. In this write-up I will walk through the background, the options I
considered, and a detailed rationale for each edit.

# ✅ GOOD
Updated `src/costs.py` so round-trip cost uses the same bps as the hurdle
check. Tests: `uv run pytest tests/test_citation_card.py`.
```

## Cursor vs billed quota

Maximise token quota efficiency. Cursor-included models (including Grok) are the default for **all** work. Non-Cursor, non-Grok models (Claude, Gemini, and other billed models) cost quota: use them only when their judgment is worth it, and only for that slice.

Do not use a billed model as the parent agent. If this session is already a billed parent, do not launch more billed sub-agents; ask the user to switch the parent to a Cursor model.

A billed model runs **only as a packed sub-agent**. The Cursor parent keeps everything a Cursor model can finish: exploration, packing, I/O, applying results, retries.

### When to launch a billed model

Launch only when a Cursor model cannot do the job well enough. Do not launch for search, grep, mechanical edits, script runs, web fetches, or work the parent already knows how to finish.

### Pack the billed slice only

Before starting a billed sub-agent, the Cursor parent does the cheap work:

1. Search, read, and finish any part a Cursor model can finish.
2. Write a prompt with one job, a **complete fact picture**, and what to return. Pack means compact, not thin: include every constraint, decision, path, and quote the sub-agent needs. Do not omit facts to save tokens. Do not send work the billed model should not do.
3. Do not forward chat history, these guidelines, whole files, or long logs. Point to paths and symbols; quote only the lines that matter.

```text
# ❌ BAD
Launch a billed model as the parent, or pass it five full modules plus the
last three chat turns. Or pass a one-liner that leaves out constraints.

# ✅ GOOD
Cursor parent finds the cost module, then launches a billed sub-agent with:
Job: check round-trip cost vs hurdle. Path: src/costs.py, function
round_trip_bps. Constraint: hurdle uses the same bps; do not change the
hurdle formula. Quote: `cost_bps = 2 * one_way_bps`. Return: file, function,
and whether they match. Do not paste the whole file.
```

### Cursor models do cheap work, including I/O

Repo reads and writes, tool calls, script execution, web searches, MCP, retries, applying patches, and any other third-party input go through a Cursor-included model. The billed sub-agent works from packed facts and returns:

- the decision, draft, or patch as text, or
- a precise I/O request: paths to read, commands to run, searches to make

The Cursor parent executes that request, then applies the result or re-packs and continues. The billed model may do that cheap work itself **only** when the Cursor parent cannot.

```text
# ❌ BAD
Billed sub-agent greps the repo, fetches a producer page, runs pytest, then
writes the file.

# ✅ GOOD
Cursor parent packed the quotes. Billed sub-agent returns the patch text
and "run uv run pytest tests/test_citation_card.py". Parent writes and runs.
```
