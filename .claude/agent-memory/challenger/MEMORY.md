# Challenger memory: how to challenge

## Where weak samples hide
- Read every "Sample:" recipe line in audit-program.md. "Largest first" with no stratum is the most common weakness: it draws long-standing big suppliers that likely hold old contracts and misses the band where the indicator is sharpest (spend just over a threshold, lower annualised bands).
- Compare a test's sample size with the population count in analytics.json. If the population is about 12 or fewer, ask for all of it; the register's own "fully testable" wording is good evidence.
- Check the sample tables for payees that are not purchases (public bodies, trust or fundraising accounts). The inter-authority exclusion can let council payees through when the narrative says private contractors.
- Check for concentration: several groups from one supplier in one test. Ask for "one item per supplier_norm" and cite a sibling test that already uses it.
- When a rating uplift cites an adverse opinion (history.json), check that some sample actually reaches that theme.

## Rating challenges
- The off_contract top20 list in analytics.json can show many suppliers above a higher threshold. Use it to test ratings that rest on a single small count.
- Rating points always end "for the auditor"; the planner will not change the plan for them.

## Coverage challenges
- Compare the register's "Excluded" section and tag totals (grants, agency staff) with the memo Limitations.
- Test each "not tested" reason in the memo against evidence lists the pack already requests.

## Wording and process
- Asks phrased as an exact recipe change (stratum bounds, per-supplier limit, replace-next rule) were accepted in one round.
- The builder's exclude-drawn-in only sees earlier tests, so asks to exclude a later test's suppliers get declined. Phrase cross-test overlap asks the other way round, or skip them.
- Use Read on challenges.md before rewriting it. A Write without a prior Read fails, and a missed error means the file was not updated.
