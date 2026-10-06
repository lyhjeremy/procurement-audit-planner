# Step 1.2 follow-up: "What do you know about this project?"

The guide asks this right after `CLAUDE.md` is written. We missed it at the
time and asked it during the final review on 2026-10-06, in a fresh session
that read only `CLAUDE.md` and listed the folder. By then the project was
built, so the answer reports nothing missing except the optional
procurement-card data. The answer, unedited:

> This is an agentic planner for a West Berkshire Council procurement audit. It turns the council's Contract Procedure Rules into testable rules, analyses the full spend population against them, adds past audit history, rates the risks, and produces a cross-checked planning pack for a human auditor to approve.
>
> The flow has six steps:
> 1. The `/extract-rules` skill converts the rules PDF into `rules.json`.
> 2. The `spend-analyst` sub-agent runs Python tests on the spend workbooks and `contracts.csv`. The tests cover threshold clustering, split purchases, off-contract spend, duplicates, expired notices and spend against award. In parallel, `findings-analyst` reads the committee papers into `history.json`.
> 3. `risk-assessor` merges these into `risk-register.md`, using the `risk-assessment` skill.
> 4. The auditor approves or rejects the risks (first human gate).
> 5. An agent team (`planner`, `challenger`, `qa-reviewer`) builds the memo, risk-control matrix and audit program, then runs the QA scripts.
> 6. The auditor signs off the pack (second human gate).
>
> The design principles are:
> - The LLM judges, and Python computes every number.
> - Everything is traceable to a quote, metric or prior finding.
> - Outputs are risk indicators, never accusations.
> - Agents never load full datasets into context.
> - Missing or malformed input means stop and report, never fabricate.
>
> The folder looks fully built. Inputs are in `data/`. The scripts exist: `clean.py`, `analyse.py`, `verify_history.py`, `selfcheck.py` and `scripts/checks/`. Every output named in the brief is in `outputs/`, from `rules.json` through `review.md`. Beyond the brief, it also has a `deploy/` folder (Dockerfile, fly.toml), `docs/`, a README and a `.venv`. I haven't opened the outputs, so I can't confirm the pack passes QA or that the final sign-off block is completed. The only gap in the brief itself is that the optional procurement-card data (`data/pcard/`) isn't present.
