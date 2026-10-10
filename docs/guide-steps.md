# Guide steps: what was done

Every step of the build guide at https://procurement-audit-planner.vercel.app/,
in order, with what was done and where the evidence is. The guide's prompts are
saved word for word in `docs/guide-prompts/` (file names start with the step
number).

How the steps were run: the guide expects each prompt to be pasted into a
Claude Code session opened in the project folder. Here one Claude Code session
(Claude Code 2.1.291) acted as that session. It wrote setup files itself and
ran each skill and sub-agent by starting a sub-agent that read the project's
own `CLAUDE.md` and the skill or agent file, and followed it. Where the guide
offers "copy the finished file" or "ask Claude to write it", we copied the
finished file; the one step with no finished file (3.5) was written from the
guide's prompt.

## Setup

| Step | What the guide asks | What was done | Evidence |
|---|---|---|---|
| Pre | VS Code installed | Claude Code CLI used directly; the editor is not part of the build | n/a |
| Pre | Claude Code installed and signed in | Claude Code 2.1.291, signed in | n/a |
| 1.1 | Make the folder, start Claude Code | Folder `procurement-audit-planner` created outside Google Drive | this repo |
| 1.2 | Hand over the project brief, then ask "What do you know about this project?" | `CLAUDE.md` written with the guide's content exactly (313 lines). The follow-up question was missed at the time and asked during the final review; the answer summarises the system and its principles | `CLAUDE.md`, `docs/step-1.2-answer.md` |
| 1.3 | Download the data folder | `data.zip` from the guide unzipped to `data/` (3 workbooks, 4 committee PDFs, rules PDF, contracts CSV) | `data/` |
| 1.4 | Set up Python and check the data | `.venv` with pandas and openpyxl, `requirements.txt`; poppler present. Check found 10,607 spend rows, header on row 1 in P02 and row 2 in P03/P04, dates already datetime, 141 of 150 contract rows are the council's under 3 spellings (one upper-case) | `requirements.txt` |
| 1.5 | Create the project folders | `.claude/skills`, `.claude/agents`, `scripts`, `outputs` | repo tree |

## Lesson 1: skills

| Step | What the guide asks | What was done | Evidence |
|---|---|---|---|
| 2.1 | Build the extract-rules skill | Copied the finished `SKILL.md` and `verify_quotes.py` | `.claude/skills/extract-rules/` |
| 2.2 | Run `/extract-rules` | 65 rules, 99 excluded clauses, 4 threshold parameters left null; verifier prints `ALL CHECKS PASSED (65 rules, 99 excluded, 0 warning(s))`. On 2026-10-09, at the auditor's direction, clause 1.6.2 (a grant is a contract) moved from excluded to CPR-66, appended so the other IDs keep their numbers (see the second gate round below); the verifier then prints `66 rules, 98 excluded` | `outputs/rules.json` |

## Lesson 2: sub-agents

| Step | What the guide asks | What was done | Evidence |
|---|---|---|---|
| 3.1 | Build the spend-analyst | Copied the finished agent file | `.claude/agents/spend-analyst.md` |
| 3.2 | Run the spend-analyst | 10,607 rows read, 8,534 kept; 7 tests run with thresholds taken from `rules.json`; the agent wrote and ran `clean.py`, `analyse.py` and `selfcheck.py` (8 of 8 re-derivations matched). Re-run on 2026-10-09 after CPR-66 was added, with `analyse.py` changed to cite it: every figure identical, self-check 0 failures | `outputs/analytics.json`, `outputs/analytics-full/`, `scripts/` |
| 3.3 | Build the findings-analyst | Copied the finished agent file and `verify_history.py` | `.claude/agents/findings-analyst.md`, `scripts/verify_history.py` |
| 3.4 | Run it and check three items visually | 20 audit entries (16 audits, 3 follow-ups, 1 advisory review), 10 risk themes, the council's 5x5 scoring method, 13 discrepancies; verifier passed (130 quotes). One audit opinion, one impact-scale entry and one risk band were checked against rendered PDF pages: all three matched | `outputs/history.json` |
| 3.5 | Build the risk-assessment skill | No finished file is offered for this step, so it was written from the guide's prompt: `SKILL.md` (method, theme table, likelihood rubric, impact method, ratings format) and `build_register.py` (resolves citations, fills placeholders, scores on the council's matrix, drops untraceable risks, writes the decision template, enforces revisions). Tested on a fixture with one good and one broken risk, and on a revision with an unrequested change | `.claude/skills/risk-assessment/` |
| 3.6 | Build the risk-assessor | Copied the finished agent file; `CLAUDE.md` already names it at step (3), so no edit was needed | `.claude/agents/risk-assessor.md` |
| 3.7 | Run it and review the register | 10 risks rated, builder `warnings: 0, failures: 0`; builder rerun by the lead; no supplier name in any risk statement or justification (checked against 181 normalised supplier names) | `outputs/risk-register.md`, `outputs/risk-ratings.json` |

## Lesson 3: the human gate

| Step | What the guide asks | What was done | Evidence |
|---|---|---|---|
| 4.1 | Open the decision template | 10 rows, one per risk, all blank | `outputs/auditor-comments.md` |
| 4.2 | Record your decisions | Jeremy Lee, 2026-10-06: approve R-02 to R-09; amend R-01 (bring into scope); reject R-10 (covered by R-04) | `outputs/auditor-comments.md` |
| 4.3 | Revise the register | Revision 1 written by the builder: R-01 amended, R-10 rejected and moved to excluded; `build_pack.py --gate` reports the gate closed | `outputs/risk-register.md`, `outputs/.register-versions/` |
| 4.2 (second round) | Record your decisions | Jeremy Lee, 2026-10-09, after comparing with a teammate's build: amend R-04 to bring in grant suppliers (clause 1.6.2, now CPR-66) and agency-staff suppliers with no live notice, and exclude premises costs as property costs; R-01 now approve (its amendment stands); others unchanged | `outputs/auditor-comments.md` |
| 4.3 (second round) | Revise the register | Revision 2 by the risk-assessor: R-04 amended (still 3 x 5 = 15, now citing grant and agency-staff figures and CPR-66), premises added to Excluded, the grants exclusion removed, every other risk unchanged against the v1 snapshot; builder `warnings: 0, failures: 0`; gate closed at revision 2 | `outputs/risk-register.md`, `outputs/.register-versions/v2.json` |

## Lesson 4: agent teams

| Step | What the guide asks | What was done | Evidence |
|---|---|---|---|
| 5.1 | Close the gate | No decision was blank, so nothing to fill; gate check passes (revision 1, then revision 2) | `build_pack.py --gate` |
| 5.2 | Enable agent teams | `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in the env block | `.claude/settings.json` |
| 5.3 | Build the audit-program skill | Copied the finished `SKILL.md` and `build_pack.py` | `.claude/skills/audit-program/` |
| 5.4 | Build the planner | Copied the finished agent file | `.claude/agents/planner.md` |
| 5.5 | Build the challenger | Copied the finished agent file | `.claude/agents/challenger.md` |
| 5.6 | Build the qa-reviewer and its checks | Copied the finished agent file and the five check scripts | `.claude/agents/qa-reviewer.md`, `scripts/checks/` |
| 5.7 | Run the team | Final run on 2026-10-09 (register revision 2). Planner, challenger and qa-reviewer ran from their agent files and messaged each other directly with SendMessage (20 messages between them); the lead only passed addresses, two status checks and one answer. Three pack versions; 8 challenges in two rounds, all resolved, none for the auditor; QA failed v2 and the first v3 run only on the trace check (challenges still open) and the final v3 run passed all four checks. The first run (2026-10-06, revision 1) is in the git history | `outputs/planning-memo.md`, `outputs/risk-control-matrix.md`, `outputs/audit-program.md`, `outputs/samples/`, `outputs/challenges.md`, `outputs/review.md`, `docs/team-messages.md` |
| 5.8 | Sign off | Verdict READY FOR SIGN-OFF (4 of 4); Jeremy Lee signed off on 2026-10-09, noting two questions for the council at fieldwork (DSG-funded early-years payments under CPR-66, and the completeness of the children's direct-payment list). The first run was signed off on 2026-10-06 | `outputs/review.md` |

**Note on step 5.7.** Claude Code's interactive agent-team mode needs an
interactive terminal. In the final run the lead session started the three
agents as background agents, each following its file in `.claude/agents/`,
and gave each the other two addresses; from then on they messaged each other
directly with SendMessage, as the deployed harness (Part B) does. Starting a
separate interactive session for true teammates was blocked by Claude Code's
permission check. The protocol (PACK READY, CHALLENGE, RESPONSE, QA FAIL, DONE)
and the agent files are exactly the guide's. Every message is in
`docs/team-messages.md`. In the first run (2026-10-06) the lead delivered the
messages instead; that log is in the file's git history.
