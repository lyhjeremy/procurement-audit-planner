# Planner memory (how-to only)

- analytics-full file names differ from the skill's examples: split windows are `split-purchases.csv` and duplicate groups `duplicates.csv`; neither has a `window_id`/`group_id`, so set `"key": "supplier_norm"` on `groups` samples.
- Split-purchase windows for large contractors can hold dozens of payments; without `per_group_n` (5 works) a ten-window sample balloons to ~175 transactions.
- `spend-vs-award.csv` has no flag column: filter with `where_min: {"ratio": 1.25}`.
- The literal-figure check (`£` + digit, or any 3+ digit number) runs on objectives, controls, steps, evidence and memo text. Write thresholds as words ("the three-quote threshold") or `£{{$.thresholds[1].value}}`; years such as a four-digit date also trip it.
- `exclude_drawn_in` only sees tests earlier in plan order, and excludes whole suppliers, not just rows.
- For R-03-style award tracing, `off-contract.csv` with `match_class = exact` gives suppliers that have a notice to trace; unmatched ones belong to the off-contract risk.
- Challenger expectations seen: exclude public-body payees from procurement samples (`where_not_match` on the supplier column with `$.population.tag_regexes.inter_authority_supplier`, plus `|FUNDRAISING` for trust accounts); test small flagged populations (about 12 or fewer) in full; use `distinct_by: supplier_norm` on every group or row sample; split the top-risk supplier sample into a largest stratum and a low-band stratum.
- Direct payments are identifiable only by Narrative "Direct Payment" (Adult Social Care, tagged general_procurement), and there are very few suppliers behind them.
