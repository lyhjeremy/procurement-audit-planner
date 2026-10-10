# QA review of the audit planning pack

Pack version checked: v3 on register revision 2 (PACK READY v3; PLANNER DONE v3 and CHALLENGER DONE confirmed by the lead)
Date: 2026-10-09
Command: `.venv/bin/python scripts/checks/run_checks.py` (exit 0)

## Check results

| Check | Result | Counts as printed by the script |
| --- | --- | --- |
| quotes | PASS | rules=66 register_excerpts=23 failures=0 (verify_quotes.py: ALL CHECKS PASSED, 66 rules, 98 excluded, 0 warnings) |
| numbers | PASS | figures_checked=316 allowed_values=2368 failures=0 |
| trace | PASS | rules=66 rules_cited=39 rules_not_tested=27 approved_in_scope=9 planned=9 high_risks=6 challenges=8 open=0 failures=0 |
| samples | PASS | transactions_checked=289 in_program=268 workbooks=3 failures=0 |

## Failures

None in the final run. Earlier rounds in this run:

- v1 passed 4/4, but the trace check read the challenges.md left from the revision 1 run.
- v2 and the first v3 run failed trace with "challenges still open: #1, #2, #3, #4, #5, #6, #7".
- After the challenger closed its challenges, challenges.md held 8 challenges with 0 open, and all four checks pass on v3.

## Verdict

READY FOR SIGN-OFF (4/4 checks pass)

## Auditor sign-off

Signed off by: Jeremy Lee
Date: 2026-10-09
Decision (sign off / return to the team): sign off
Comment: No challenge is marked for the auditor. Two questions go to the council at fieldwork, as the program already says: whether the DSG-funded early-years payments in T-04.4 and T-04.5 are grants under CPR-66 or statutory allocations, and whether the council's list of children's direct payments used for T-09.3 is complete.
