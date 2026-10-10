# qa-reviewer memory (how to run the checks only)

- Run from the project root: `.venv/bin/python scripts/checks/run_checks.py`. No flags needed. It runs all four checks, prints a summary table and a VERDICT line, and exits 0 on READY FOR SIGN-OFF, 1 on BLOCKED.
- The trace check reads `outputs/challenges.md`. Before the challenger finishes it fails with "challenges.md missing" or "challenges still open: #...". That is expected on early PACK READY rounds; report it as a trace FAIL to the planner, not as QA BLOCKED ON INPUT.
- Copy the SUMMARY counts into review.md exactly as printed.
- On a re-run after a new register revision, an early trace PASS can come from the previous run's `challenges.md`, which is still on disk. Treat it as provisional until CHALLENGER DONE.
- PLANNER DONE and CHALLENGER DONE may be sent to the lead rather than to qa-reviewer. If they have not reached you, ask the lead before writing review.md.
- review.md from a previous run may carry a filled sign-off block. Read it first (Write requires a read), then replace the whole file and leave the sign-off block empty.
