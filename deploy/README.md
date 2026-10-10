# Part B: the deployed agent harness

Live at https://procurement-audit-lyh.fly.dev.

The harness runs the Part A system as a web application. It does not
re-implement the agents: every stage is a Claude Code session, started through
the Claude Agent SDK, in a fresh copy of this repository's `CLAUDE.md`,
`.claude/skills`, `.claude/agents`, `data/` and `scripts/`. That copy includes
Part A's spend scripts (`clean.py`, `analyse.py`, `selfcheck.py`) and the
agents' how-to memory in `.claude/agent-memory/`, so a live run's
spend-analyst starts from Part A's code and lessons rather than from a blank
folder; every output is still produced fresh by the run.

## What happens in a run

| Ref | Stage | How it runs |
|---|---|---|
| A1 | Extract the rules | Session prompt `/extract-rules`, the skill's slash command |
| A2 | Analyse spend and audit history | The session starts the `spend-analyst` and `findings-analyst` sub-agents in parallel |
| A3 | Rate the risks | The session starts the `risk-assessor`, then reruns the builder and checks for supplier names |
| A4 | Auditor decisions | A form. The server writes the decisions into `auditor-comments.md`; no model is involved |
| A5 | Revise the register | The `risk-assessor` applies the decisions; the harness itself runs `build_pack.py --gate`, which must pass |
| A6 | Plan, challenge and check | The lead starts `planner`, `challenger` and `qa-reviewer` as named background sub-agents that message each other with SendMessage, then reports for sign-off |
| A7 | Sign-off | A form. Signing off re-runs `scripts/checks/run_checks.py` and is refused unless all four checks pass; *return to the team* (with a comment) sends the pack back to A6 |

A stage counts as done only when the session ends without error, the files it
must produce exist, and its check passes. The checks are run by the harness,
not reported by the model: A5 runs `build_pack.py --gate` and A6 runs
`scripts/checks/run_checks.py` in the run's workspace. A BLOCKED pack therefore
never reaches the auditor: the harness first tells the lead to send the
failures back to the team, and if the checks still fail the run stops and the
retry button sends it back to the team. Anything else stops the run and shows
why.

## Code

| File | Role |
|---|---|
| `app/harness.py` | Stage list and prompts, the SDK call per stage, the event log, the two gate writers |
| `app/main.py` | FastAPI routes: run list, run state, live event stream (server-sent events), files, start, gate, sign-off |
| `app/static/index.html` | The single page: stage index, activity log, gate forms, document viewer |
| `make_reference.py` | Packages the Part A run as the read-only reference run |
| `Dockerfile`, `fly.toml` | Container and Fly.io config; built from the repo root |

SDK options for each stage: `cwd` is the run's workspace,
`setting_sources=["project"]` loads the project's settings, skills and agents,
the model is `claude-sonnet-5-5` for the lead and every sub-agent,
`permission_mode="dontAsk"` with an explicit tool allowlist (no web access),
and `max_budget_usd` caps each stage.

For the team stage the harness passes the three team agent files through the
SDK's `agents` option with `SendMessage` added to their tools. In an
interactive terminal Claude Code adds that tool to every teammate itself; a
headless session runs teammates as named sub-agents, which only get the tools
their file lists. Instructions, tools and memory still come from the files.

## Keeping a stage alive, and retrying one

Each stage runs on one connected SDK client, so background sub-agents keep
working between the lead's turns. If the lead ends a turn while the stage's
required files are still missing or its check fails, the harness waits for 60 seconds of quiet and
sends a status check (at most 4 per stage, within 45 minutes); for the team
stage the check tells the lead to collect PLANNER DONE and have the qa-reviewer
write `review.md`. A run that stops anyway shows a **Retry the stopped stage**
button (passcode), which reruns only the failed stage and keeps every file the
earlier stages wrote.

## Safeguards

- Watching runs and reading documents is open. Starting a run, recording
  decisions and signing off need `RUN_PASSCODE`.
- `RUNS_PER_DAY` caps the runs started per day (default 3). Retries and
  returns to the team spend credit too, so each counts against the same cap.
  Only one run works at a time.
- `STAGE_BUDGET_USD` caps each stage's spend (default 6). A local end-to-end
  test cost about $3.60 in total at Sonnet prices.
- Runs live on a Fly volume at `/data/runs`. A run that was working when the
  server restarted is marked as interrupted.
- The container runs as a non-root user; the API key is a Fly secret.
- The server removes `RUN_PASSCODE` from its environment at start-up, so agent
  sessions never inherit it. The Claude Code CLI needs `ANTHROPIC_API_KEY`, so
  agent Bash can see that one; the harness redacts it (and the passcode) from
  the public event log and from every file the viewer serves.
- The gate form preselects no decision: the auditor must choose approve,
  amend or reject for every risk.

## Deploy

From the repo root:

```bash
python deploy/make_reference.py             # refresh the reference run from outputs/
fly secrets set --app procurement-audit-lyh ANTHROPIC_API_KEY=... RUN_PASSCODE=...
fly deploy --config deploy/fly.toml --dockerfile deploy/Dockerfile .
```

Run locally:

```bash
python3 -m venv deploy/.venv && deploy/.venv/bin/pip install -r deploy/requirements.txt
RUN_PASSCODE=local TEMPLATE_DIR=<clean copy of the project> RUNS_DIR=/tmp/runs \
  PROJECT_VENV=$PWD/.venv REFERENCE_DIR=deploy/reference \
  deploy/.venv/bin/uvicorn app.main:app --app-dir deploy --port 8080
```
