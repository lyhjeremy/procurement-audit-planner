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
                               │ risk-assessor re-runs: one register revision per round
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
| Rules | 66 testable rules, 98 excluded clauses, 4 threshold parameters left null because the PDF only names them (3 statutory thresholds and the composite "relevant threshold"). 65 came from the skill; clause 1.6.2 (a grant is a contract) was added as CPR-66 at the second gate round |
| Spend | 10,607 payments read, 8,534 kept after excluding pension, inter-authority and redacted-payee rows; 6 indicator tests, plus the list of high-value suppliers (annualised spend of £25,000 or more) that the off-contract test runs on |
| History | 20 audit entries (16 audits, 3 follow-ups, 1 advisory review) with their opinions, including Limited on Personal Budgets (Direct Payments); 10 risk themes; the council's 5x5 scoring method; 13 discrepancies in the papers |
| Register | 10 risks rated; the builder marks, without resolving, the conflict between Figure 4 (corporate register at 9 or above) and Table 4 (15 or above) |
| Gate | Two rounds by Jeremy Lee. 2026-10-06: approved 8, amended R-01 into scope, rejected R-10 (revision 1). 2026-10-09: amended R-04 to add grants and agency staff, excluded premises (revision 2) |
| Team | Final run on revision 2: 3 pack versions, 8 challenges over 2 rounds (all resolved, none for the auditor), the three agents messaging each other directly; QA verdict READY FOR SIGN-OFF with 4 of 4 checks passing |
| Pack | 9 risks, 12 controls, 24 tests, 289 sample rows covering 268 distinct payments (21 payments are drawn by two tests), each traced to its row in the published workbooks; 39 of 66 rules cited and the other 27 listed as not tested with a reason |
| Sign-off | Signed off on 2026-10-09, with two questions noted for the council at fieldwork |

The outputs are all in `outputs/`. Start with
[outputs/planning-memo.md](outputs/planning-memo.md).

## Confirmation of the guide steps

We completed every step of the guide: setup 1.1 to 1.5, skills 2.1 and 2.2,
sub-agents 3.1 to 3.7, the human gate 4.1 to 4.3 and agent teams 5.1 to 5.8.
[docs/guide-steps.md](docs/guide-steps.md) lists each step with what was done
and the file that shows it, and the guide's prompts are saved in
`docs/guide-prompts/`.

Four things differ from a plain run of the guide, and the step list says so.
The `risk-assessment` skill (step 3.5) has no finished file in the guide, so
we wrote it from the guide's prompt. The step 1.2 follow-up question was
asked during the final review rather than straight after step 1.2
([docs/step-1.2-answer.md](docs/step-1.2-answer.md)). Rule CPR-66 was added to
`rules.json` by hand at the auditor's direction (see below), and
`verify_quotes.py` passes with it. And for step 5.7, Claude Code's
interactive agent-team mode needs an interactive terminal; in the session we
used, the three team agents ran as background agents from their files and
messaged each other directly with SendMessage, the same way the deployed
harness runs them ([docs/team-messages.md](docs/team-messages.md)).

## Auditor judgment and reflection

### Gate decisions and why

First round (2026-10-06):

| Risk | Decision | Reason |
|---|---|---|
| R-01, quotes not sought just below the thresholds | amend: bring into scope | Threshold-hugging at the £25,000 quote boundary is a standard test and cheap to sample; the rating stays |
| R-10, contract register incomplete | reject | R-04 reconciles unmatched suppliers to the contract register, which already tests its completeness |
| R-02 to R-09 | approve | Ratings and evidence accepted as written |

Second round (2026-10-09): R-04 amended. A teammate's independent build of
the same guide (Neil Doungsaeng, https://github.com/neiltd/procurement-audit-planner)
kept grants in scope where ours left them out. Clause 1.6.2 lists "Providing
funding or a grant to an external organisation" as entering a contract, so
grant spend falls under the Rules. Our first register excluded grants only
because the extract-rules skill files definitions as untestable, which left
no rule ID to cite. The guide's own spend-analyst file says the opposite
("clause 1.6.2 treats a grant as a contract. Cite these by `rule_id`"). We
added 1.6.2 as CPR-66 and brought into R-04 the 123 grant suppliers and the 1
agency-staff supplier with no live contract notice. Agency staff is a bought
service. Premises costs (rent, rates, leases) stay out because they are
property costs, not purchases under the Rules, and the register now says so.
R-04's rating did not move (3 x 5 = 15).

### Sign-off

The first pack was signed off on 2026-10-06 with challenge #2 (R-03
likelihood) noted and not taken up: R-03 was already in scope, and T-04.2
tested the Appendix A approval for unmatched suppliers above the Key Decision
threshold, so a higher score would not have changed the fieldwork. The final
pack was signed off on 2026-10-09 with no challenge left for the auditor. Two
questions go to the council at fieldwork: whether the DSG-funded early-years
payments sampled in T-04.4 and T-04.5 are grants under CPR-66 or statutory
allocations, and whether the council's list of children's direct payments
used in T-09.3 is complete.

### What the human gate changed

- R-01 entered scope, which added a threshold-hugging test.
- R-10 was folded into R-04 instead of being planned twice.
- The second round put £5.87M of grant spend (123 suppliers) and £1.28M of
  agency-staff spend under test. The rebuilt pack has 7 more tests (24 against
  17) and 60 more sample rows (289 against 229).

### What we would do differently

- Read every skill and agent file against the others before the first run.
  The 1.6.2 conflict sat between two of the guide's own files and only
  showed up when a second build disagreed with ours.
- Compare with an independent build earlier. Two people building the same
  guide disagreed on scope, and that disagreement found the gap.
- Have each teammate send its DONE message to the other two as well as to the
  lead. In our final run the qa-reviewer waited for DONE messages that had
  gone only to the lead, so the lead had to tell it both had finished. The
  deployed harness already nudges a lead that goes quiet, for a similar
  reason.

### Part A compared with Part B

Part A was built and run step by step in one Claude Code session, with the
person at the keyboard making both gate decisions in files. Part B runs the
same `CLAUDE.md`, skills and agents unchanged through the Claude Agent SDK,
one stage at a time, with the two gates as web forms, a passcode and a
spending cap. A full Part B run cost $3.68 to $4.45. Part B starts each run from
the guide's skills, so its extract-rules stage files clause 1.6.2 as a
definition again; the auditor at the gate decides how grants are treated,
as we did in round two.

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

The site holds two complete live runs made by the deployed harness itself, both
signed off:

- **Live Run 1** (6 to 7 Oct 2026, $4.45): all seven stages. Its team stage first
  stopped early (the lead ended its session while teammates were finishing); the
  harness now keeps each stage's session open, nudges a lead that goes quiet,
  and can retry a stopped stage, which is how that run finished.
- **Live Run 2** (10 Oct 2026, $3.68, about 10 minutes of agent time): all seven
  stages with no retry. At the gate Jeremy Lee approved 6 risks, amended 2
  (lowered the likelihood of the off-contract and duplicate-payment risks,
  which had been rated 4 on weaker evidence) and rejected 1 (award approvals,
  covered by the off-contract tests). The team then went through 3 pack
  versions and 10 challenges, all resolved; QA passed 4 of 4 checks; signed
  off the same day.

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
skills and agents are already in place. The quote checks need poppler's
`pdftotext` specifically; they stop with a clear message if they find another
one. On Windows, Git for Windows puts xpdf's `pdftotext` on the PATH, so
install poppler and set `PDFTOTEXT` to its `pdftotext.exe`; the venv's Python
is `.venv\Scripts\python.exe` rather than `.venv/bin/python`.

Data: West Berkshire Council, public records (Contract Procedure Rules,
expenditure over £500, Contracts Finder notices, Governance Committee papers).
