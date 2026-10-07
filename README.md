# Procurement audit planner

MGMTMSA 440 (Building LLM Applications), Assignment 2, Lumina Group.

This repo rebuilds the reference application at
https://procurement-audit-planner.vercel.app/ with the skills and agents
architecture from class (Part A), and turns it into an independently deployed
agent harness (Part B).

The system plans an internal audit of West Berkshire Council's procurement
from public data. It turns the council's Contract Procedure Rules into
testable rules, analyses every published payment over £500 for three months,
reads past audit opinions and the council's risk scoring method from its
committee papers, rates the risks, stops for an auditor's decisions, and then
has an agent team write, challenge and check an audit plan for sign-off.

- **Part A:** this repository. The build follows every step of the guide; see
  [docs/guide-steps.md](docs/guide-steps.md).
- **Part B:** https://procurement-audit-lyh.fly.dev, the same skills and agents
  run by a web harness through the Claude Agent SDK. Code in [deploy/](deploy/).

The outputs are risk indicators to investigate, never findings of wrongdoing
by the council, a department, an officer or a supplier.

## Skills

A skill is a written method in `.claude/skills/<name>/SKILL.md`, with a Python
script beside it that checks the work, so the method is followed the same way
every time.

| Skill | Used by | What it does | Its script |
|---|---|---|---|
| `extract-rules` | the person, as `/extract-rules` | Reads `data/contract-rules.pdf` and writes `outputs/rules.json`: one entry per testable rule with clause, page, thresholds, required action, approver and a verbatim quote. Clauses that cannot be tested go to an `excluded` list with a reason; thresholds the PDF only names stay null | `verify_quotes.py` checks the schema, the rule IDs and that every quote is on the page it cites. It must print ALL CHECKS PASSED |
| `risk-assessment` | the risk-assessor | Turns rules, spend indicators and audit history into rated risks on the council's own 5x5 likelihood × impact scale. Every likelihood and impact justification must cite a rule, a metric or an audit item; figures are placeholders, never typed; a repeat finding with an adverse audit raises likelihood by one | `build_register.py` resolves every citation, fills figures from `analytics.json`, computes score, matrix label and band, drops untraceable risks, writes the register and the auditor's decision template, and on a re-run fails if a decision was not applied or something changed that the auditor did not ask for |
| `audit-program` | the planner | Turns each approved risk into expected controls, test steps, sample recipes and the documents to request from the council | `build_pack.py` checks the gate, validates the plan, draws every sample from the analytics files, checks every rule is cited or listed as not tested, and renders the planning memo, risk-control matrix and audit program |

The `risk-assessment` skill is the one the guide gives no finished file for, so
we wrote it from the guide's prompt (step 3.5), shaped to the real structure
of `analytics.json` and `history.json`. The other two are the guide's finished
files.

## Agents

Each agent is a file in `.claude/agents/` with its tools in the frontmatter
and its instructions in the body. Each has project memory in
`.claude/agent-memory/<name>/MEMORY.md`, which holds how-to lessons only, never
figures, ratings or supplier names.

| Agent | Kind | Reads | Writes |
|---|---|---|---|
| `spend-analyst` | sub-agent | `rules.json`, the three spend workbooks, `contracts.csv` | Python in `scripts/` (`clean.py`, `analyse.py`, `selfcheck.py`), `outputs/analytics.json` and full lists in `outputs/analytics-full/` |
| `findings-analyst` | sub-agent | the four committee PDFs | `outputs/history.json`: audit opinions, risk themes, the council's scoring method, gaps and discrepancies, every item with source and page |
| `risk-assessor` | sub-agent | `rules.json`, `analytics.json`, `history.json`, later `auditor-comments.md` | `outputs/risk-ratings.json`; its builder writes `risk-register.md` and `auditor-comments.md` |
| `planner` | agent-team member | the approved register, ratings, rules, analytics | `outputs/audit-plan.json`; its builder writes the three planning documents and `outputs/samples/` |
| `challenger` | agent-team member | the register, history, analytics, the pack | `outputs/challenges.md` |
| `qa-reviewer` | agent-team member | everything, through `scripts/checks/run_checks.py` | `outputs/review.md` with the verdict and the sign-off block |

## How they work together

```
contract-rules.pdf ──► /extract-rules (skill) ──► rules.json
                                                     │
            ┌────────────────────────────────────────┤
            ▼                                        ▼
  spend-analyst (sub-agent)                findings-analyst (sub-agent)
  spend xlsx + contracts.csv               committee PDFs
  writes and runs Python                   reads and quotes
            │ analytics.json                         │ history.json
            └──────────────────┬─────────────────────┘
                               ▼
              risk-assessor (sub-agent) + risk-assessment skill
                               │ risk-register.md, auditor-comments.md
                               ▼
              HUMAN GATE: auditor approves, amends or rejects each risk
                               │ risk-assessor re-runs: register revision 1
                               ▼
     agent team: planner ◄──► challenger, planner ◄──► qa-reviewer
     (audit-program skill)   (challenges.md)        (4 check scripts, review.md)
                               │ planning memo, risk-control matrix, audit program
                               ▼
              HUMAN GATE: auditor signs off in review.md
```

The files are the interfaces. Each stage reads the files the stage before it
wrote, and a script checks each hand-off. The rule throughout is that the
model reads and judges while Python computes every number: the analysts' scripts
compute the indicators, the builders fill every figure from `analytics.json`,
and the QA checks confirm that every quote is in its PDF, every figure in the
pack traces to a computed value, every rule traces to a risk, control or
test, and every sampled payment exists in the council's workbooks.

The agent team runs on a message protocol set in the agent files. The planner
announces `PACK READY vN`; the challenger sends `CHALLENGE #n` with evidence
and an ask; the planner answers `RESPONSE #n: accepted / declined / for the
auditor` and rebuilds; the qa-reviewer runs the checks on each version and
sends `QA vN: PASS/FAIL`; each ends with a DONE message to the lead.

## Results of our run

| Stage | Result |
|---|---|
| Rules | 65 testable rules, 99 excluded clauses, 4 statutory thresholds left null because the PDF only names them |
| Spend | 10,607 payments read, 8,534 kept after excluding pension, inter-authority and redacted-payee rows; 7 indicator tests |
| History | 20 audit entries (16 audits, 3 follow-ups, 1 advisory review) with their opinions, including Limited on Personal Budgets (Direct Payments); 10 risk themes; the council's 5x5 scoring method; 13 discrepancies in the papers |
| Register | 10 risks rated; the builder marks, without resolving, the conflict between Figure 4 (corporate register at 9 or above) and Table 4 (15 or above) |
| Gate | Jeremy Lee approved 8, amended R-01 into scope and rejected R-10; revision 1 |
| Team | 3 pack versions, 12 challenges over 2 rounds (11 resolved, 1 for the auditor), QA verdict READY FOR SIGN-OFF with 4 of 4 checks passing |
| Pack | 9 risks, 11 controls, 17 tests, 229 sampled payments, each traced to its row in the published workbooks; 36 of 65 rules cited and the other 29 listed as not tested with a reason |
| Sign-off | Signed off on 2026-10-06, with the open rating point (challenge #2) noted |

The outputs are all in `outputs/`. Start with
[outputs/planning-memo.md](outputs/planning-memo.md).

## Confirmation of the guide steps

We completed every step of the guide: setup 1.1 to 1.5, skills 2.1 and 2.2,
sub-agents 3.1 to 3.7, the human gate 4.1 to 4.3 and agent teams 5.1 to 5.8.
[docs/guide-steps.md](docs/guide-steps.md) lists each step with what was done
and the file that shows it, and the guide's prompts are saved in
`docs/guide-prompts/`.

Three things differ from a plain run of the guide, and the step list says so.
The `risk-assessment` skill (step 3.5) has no finished file in the guide, so
we wrote it from the guide's prompt. The step 1.2 follow-up question was
asked during the final review rather than straight after step 1.2
([docs/step-1.2-answer.md](docs/step-1.2-answer.md)). And for step 5.7, Claude Code only
spawns true teammates in an interactive terminal; in the session we used, the
three team agents ran as sub-agents and the lead delivered their protocol
messages unchanged ([docs/team-messages.md](docs/team-messages.md)). The
deployed harness runs them as named sub-agents that message each other
directly.

## Part B: the deployed harness

https://procurement-audit-lyh.fly.dev runs the whole workflow without anyone's
laptop:

- Each stage is a Claude Code session started by a FastAPI server through the
  Claude Agent SDK, in a fresh copy of this project. The sessions load this
  repo's `CLAUDE.md`, skills and agents (`setting_sources=["project"]`), so the
  deployed system is the Part A system, not a rewrite.
- The pages show each stage live: which agent is working, its commands, the
  sub-agents it starts and the messages between team members.
- Both human gates are forms. The decision form writes `auditor-comments.md`;
  the sign-off form fills the sign-off block in `review.md`, and only when the
  QA verdict is READY FOR SIGN-OFF.
- Starting a run and the two gates need the team passcode, runs are capped
  per day, and each stage has a spending cap, because every run spends API
  credit. The Part A run is shown read-only as the reference run, so the site
  shows the complete workflow at any time.

The site holds one complete live run made by the deployed harness itself
("Live Run 1", 6 to 7 Oct 2026): all seven stages, including both human gates,
signed off, about $4.45 of API credit. Its team stage first stopped early (the
lead ended its session while teammates were finishing); the harness now keeps
each stage's session open, nudges a lead that goes quiet, and can retry a
stopped stage, which is how that run finished.

Details and deployment steps are in [deploy/README.md](deploy/README.md).

## Repository layout

```
CLAUDE.md                 the project brief from the guide
data/                     public inputs (read-only)
.claude/skills/           extract-rules, risk-assessment, audit-program
.claude/agents/           the six agents
.claude/agent-memory/     per-agent how-to memory
.claude/settings.json     agent teams switch (step 5.2)
scripts/                  spend-analyst Python, verify_history.py, checks/
outputs/                  everything the run produced
docs/                     guide steps, guide prompts, team message log, step 1.2 answer
deploy/                   Part B harness: FastAPI app, Dockerfile, fly.toml
```

To run Part A yourself: clone, `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`,
install poppler, open the folder in Claude Code and follow the guide; the
skills and agents are already in place.

Data: West Berkshire Council, public records (Contract Procedure Rules,
expenditure over £500, Contracts Finder notices, Governance Committee papers).
