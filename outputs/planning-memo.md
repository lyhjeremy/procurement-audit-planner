# Procurement audit: planning memo

*Generated 2026-10-06 by `build_pack.py` from `audit-plan.json`, `risk-register.md` (revision 1), `auditor-comments.md` by Jeremy Lee dated 2026-10-06, `rules.json` and `analytics.json`. Status: DRAFT for challenge, QA review and auditor sign-off.*

**Indicators, not findings.** Every test below checks a control against a pattern in public data. Nothing here asserts wrongdoing by the council, a department, an officer or a supplier.

## Purpose

This audit tests whether the controls in the Contract Procedure Rules operate over the purchasing patterns that the council's published spend data flags. Each pattern is a risk indicator to investigate, not a finding: a flagged payment may have a contract, a framework call-off or an approved waiver behind it that the public data cannot show.
The audit covers the nine risks the auditor approved at the gate. For each it asks whether the control the Rules require was in place for the sampled transactions.

## Background

The population is 8,534 payments over the publication floor, worth £66,778,104.78, across 3 months from 2026-05-01 to 2026-07-31 [metric:$.population.rows_after_exclusions] [metric:$.population.total_gbp]. Statutory pension contributions, inter-authority payments and payments to a redacted payee were excluded before testing.
General procurement accounts for £28,318,367.76 with 518 suppliers, and care and education placements for £30,571,711.30 with 361 suppliers [metric:$.population.tags.general_procurement.gbp] [metric:$.population.tags.care_or_education_placement.gbp]. Placements are exempt from competition under the Rules and are tested only for the record of provider choice.
The Contracts Finder export held 141 council notices, of which 62 were active in the spend window [metric:$.contracts.notices] [metric:$.contracts.active_in_window]. It is a list of published notices, not the council's contract register, which was not available to the planning stage.

## Scope

The register lists 9 rated risks. The auditor recorded 10 decisions by Jeremy Lee dated 2026-10-06: 9 risks are approved and in scope, and 1 is not.

| ID | Risk | Score | Band | Decision | Auditor comment |
|---|---|---|---|---|---|
| R-01 | Quotes not sought for payments just below the quotation thresholds | 6 | Moderate | amend | Bring into scope. Threshold-hugging at the £25,000 quote boundary is a standard test and cheap to sample; keep the rating as it is. |
| R-02 | Requirements split into payments that each stay under the quotation threshold | 12 | Medium - High | approve |  |
| R-03 | High-value awards made without Key Decision or the approvals in Appendix A | 10 | Medium - High | approve |  |
| R-04 | Spend above the quotation threshold with no published contract notice | 15 | Extreme | approve |  |
| R-05 | Duplicate or repeated payments of the same amount | 9 | Medium - High | approve |  |
| R-06 | Spend continuing after the published contract has ended | 6 | Moderate | approve |  |
| R-07 | Spend running above the awarded contract value without an approved variation | 12 | Medium - High | approve |  |
| R-08 | Waivers and exceptions granted without the required approval | 6 | Moderate | approve |  |
| R-09 | Care and education placements without the recorded reasons for provider choice | 12 | Medium - High | approve |  |

**Not in scope**

- R-10: Contract register incomplete or awards not notified to it: reject; Auditor: Covered by R-04: reconciling unmatched suppliers to the contract register already tests its completeness.

## Approach

The Rules were converted into testable rules with clause references. Python scripts then tested the full payment population against them for threshold clustering, split purchases, spend with no matching notice, repeated payments, spend after a notice ended and spend above the award rate. Past audit opinions and the council's risk scoring method came from the Governance Committee papers.
Each risk was rated on the council's likelihood and impact scale with every rating citing a rule, a metric or a prior audit, and the auditor approved the scope at the gate. For each approved risk this pack names the control the Rules require, a test step and a targeted sample. Samples are drawn by script from the flagged lists rather than at random, sized at ten items for risks scoring nine or more and five otherwise, and every sampled transaction is traced to its row in the published workbooks.

The programme holds 11 expected controls and 17 test steps, with 229 sampled transactions worth £18,823,142.64, each traceable to its row in the council's published workbooks (see `audit-program.md` and `outputs/samples/`).

## Rules coverage

36 of 65 rules in `rules.json` are cited by a risk, a control or a test. The remaining 29 are not tested in this audit, for these reasons:

- statutory tier: the Threshold parameter is null in rules.json, so the analytics skipped it and no risk was rated on it: CPR-08, CPR-11, CPR-26, CPR-27, CPR-45, CPR-57
- tender handling inside the Procurement Portal (format, late tenders, opening); no tender records in the inputs and no risk rated on it: CPR-12, CPR-13, CPR-14
- contract drafting and terms (written form, standard clauses, data protection, payment terms, indemnities, bonds, insurance); checked on contract files, outside the spend-pattern risks the auditor approved: CPR-30, CPR-31, CPR-33, CPR-34, CPR-35, CPR-36, CPR-37, CPR-38, CPR-39, CPR-40, CPR-41
- custody of the Seal, execution of documents and instruction of Counsel; legal governance with no link to procurement spend: CPR-42, CPR-43, CPR-44, CPR-46, CPR-47, CPR-48
- budget provision and monthly board reporting; governance steps outside the spend data with no risk rated on them: CPR-01, CPR-06
- publication of expenditure over the floor; met by the published workbooks this audit uses as its population: CPR-03

## Limitations

- The data covers payments over the publication floor only, so split-purchase and duplicate counts are lower bounds [metric:$.tests.split_purchases.parameters.lower_bound_note].
- Annual figures are annualised estimates: the window total multiplied by 4, with no adjustment for seasonal or one-off spend [metric:$.population.annualisation_factor].
- Contracts Finder holds published notices only; earlier awards, framework call-offs under another buyer and exempt placements will not appear, so an unmatched supplier is an indicator to reconcile, not evidence of spend without a contract [metric:$.tests.off_contract.register_present].
- Award values in notices may be estimates or maxima, so a high spend-to-award ratio needs confirming against the signed contract [metric:$.tests.spend_vs_award.parameters.ratio_flag].
- The statutory procurement thresholds are null in the extracted rules, so no test covers the statutory tier; above-threshold tender duties are not tested.
- Net amounts exclude VAT, and the Rules are ambiguous on whether thresholds include it; payments near a threshold may sit on either side of it.
- Waivers, exceptions, award approvals and case notes are not in the published data; those tests depend on records the council provides.
- Direct payments are identifiable in the spend data only through the Adult Social Care narrative 'Direct Payment'; direct payments for children cannot be identified, so that part of the Personal Budgets theme is not sampled.
- Grant spend (£6,033,599.82 in the window) and agency-staff spend (£1,285,541.24) are outside the tests: grants are tagged separately because the clause that would bring a grant within the Rules is a definition with no rule to cite, and agency-staff spend was not rated as a risk [metric:$.population.tags.grant.gbp] [metric:$.population.tags.agency_staff.gbp].

## Review and sign-off

The challenger's points and their status are in `challenges.md`; points marked *for the auditor* need a decision at sign-off. The QA reviewer's checks and verdict are in `review.md`, which ends with the sign-off block.
