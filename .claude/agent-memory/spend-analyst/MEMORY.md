# spend-analyst memory (method only, no figures)

- 2026-10-06 Spend header row varies by workbook (row 1 in one, row 2 in others). Find the row whose first cell is `Service`; sheet_row = 0-based header index + 2 + data index.
- 2026-10-06 Spend `Date` arrives as datetime from openpyxl; a period workbook can run a few days into the next calendar month, so count months from pay_date, not from file names.
- 2026-10-06 contracts.csv packed supplier column is named `Supplier [Name|Address|Ref type|Ref Number|Is SME|Is VCSE]`, not `Supplier`. Look it up by prefix `Supplier [`.
- 2026-10-06 Organisation Name has case and short-name variants of the council; filter with lower().strip() against a set.
- 2026-10-06 `OJEU Procedure Type` values carry a trailing space; strip before use.
- 2026-10-06 Inter-authority regex with a capturing group triggers a pandas UserWarning; use `(?:...)`.
- 2026-10-06 Inter-authority regex word COUNTY also catches non-public bodies whose name contains it (e.g. a county sports partnership). Reported as a warning, not patched.
- 2026-10-06 `T/A` normaliser misses variants written `T.A` / `T AS`; such names keep the trading-as suffix and only reach near_contain. Check near-matches.csv for these.
- 2026-10-06 rules.json: a £1,000 band requires a single quote. Treated as not competition-triggering (competition = tender, invitations to quote, or at least three/five sources); otherwise split and high-value tests become the whole population. Auditor has not ruled on this yet.
