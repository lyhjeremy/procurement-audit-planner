# Challenger memory: how to challenge

## Where weak samples hide
- Read every "Sample:" recipe line in audit-program.md. "Largest first" with no stratum is the most common weakness: it draws long-standing big suppliers that likely hold old contracts and misses the band where the indicator is sharpest (spend just over a threshold, lower annualised bands).
- Compare a test's sample size with the population count in analytics.json. If the population is about 12 or fewer, ask for all of it; the register's own "fully testable" wording is good evidence.
- Check the sample tables for payees that are not purchases (public bodies, trust or fundraising accounts). The inter-authority exclusion can let council payees through when the narrative says private contractors.
- Check for concentration: several groups from one supplier in one test. Ask for "one item per supplier_norm" and cite a sibling test that already uses it.
- When a rating uplift cites an adverse opinion (history.json), check that some sample actually reaches that theme. Compare the history item's "service" field with the Service column of the sample rows: a theme can match while the service does not. Where the data cannot identify the items, ask for a PBC list plus a fieldwork-selected sample; the planner accepts that.
- Check the stratum bounds for gaps: a top-N "largest first" test plus a capped lower band leaves the middle band unsampled. Name the missing band by the Appendix A row it falls in.
- Check the Service column for concentration as well as the supplier: a largest-first grant sample can come entirely from one funding run. Ask for "one item per top_service".
- Largest single payments to multi-user providers (placements) need an invoice-breakdown rule, or the test cannot show a pass or a fail.
- After an auditor amendment widens a risk (a new tag brought into scope), check every sibling test of that risk, and of the other risks, for the new tag; split and duplicate tests often still filter on the old tag only.

## Rating challenges
- The off_contract top20 list in analytics.json can show many suppliers above a higher threshold. Use it to test ratings that rest on a single small count.
- Rating points always end "for the auditor"; the planner will not change the plan for them.

## Coverage challenges
- Compare the register's "Excluded" section and tag totals (grants, agency staff) with the memo Limitations.
- Test each "not tested" reason in the memo against evidence lists the pack already requests. Rules checked "on contract files" fall when a test already pulls the contract.
- Check population.excluded in analytics.json (for example redacted payees) against the memo Limitations; Background mention alone is not enough.
- After the planner adds a test, re-read the memo Limitations and the old test text for sentences the new test contradicts. Round two often finds only this.

## Wording and process
- Asks phrased as an exact recipe change (stratum bounds, per-supplier limit, replace-next rule) were accepted in one round.
- The builder's exclude-drawn-in only sees earlier tests, so asks to exclude a later test's suppliers get declined. Phrase cross-test overlap asks the other way round, or skip them.
- Do not cite PBC item numbers in asks or in the file; they renumber when tests are added. Cite test IDs.
- Asks that name wording from a source not in the inputs (for example Transparency Code exemptions) get declined. Keep asks to what the inputs hold.
- Glob and Grep may be missing from the session. analytics.json is too large for Read past the top; a read-only Bash/python summary of tests.* (without top20 and row_ids) is the practical substitute.
- Use Read on challenges.md before rewriting it. A Write without a prior Read fails, and a missed error means the file was not updated.
