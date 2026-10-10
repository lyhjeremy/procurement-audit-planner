# Procurement audit: planning memo

*Generated 2026-10-09 by `build_pack.py` from `audit-plan.json`, `risk-register.md` (revision 2), `auditor-comments.md` by Jeremy Lee dated 2026-10-09, `rules.json` and `analytics.json`. Status: DRAFT for challenge, QA review and auditor sign-off.*

**Indicators, not findings.** Every test below checks a control against a pattern in public data. Nothing here asserts wrongdoing by the council, a department, an officer or a supplier.

## Purpose

This audit tests whether the controls in the Contract Procedure Rules operate over the purchasing patterns that the council's published spend data flags. Each pattern is a risk indicator to investigate, not a finding: a flagged payment may have a contract, a framework call-off or an approved waiver behind it that the public data cannot show.
The audit covers the nine risks the auditor approved at the gate on register revision 2. For each it asks whether the control the Rules require was in place for the sampled transactions.

## Background

The population is 8,534 payments over the publication floor, worth £66,778,104.78, across 3 months from 2026-05-01 to 2026-07-31 [metric:$.population.rows_after_exclusions] [metric:$.population.total_gbp]. Statutory pension contributions, inter-authority payments and payments to a redacted payee were excluded before testing.
General procurement accounts for £28,318,367.76 with 518 suppliers, and care and education placements for £30,571,711.30 with 361 suppliers [metric:$.population.tags.general_procurement.gbp] [metric:$.population.tags.care_or_education_placement.gbp]. Placements are exempt from competition under the Rules and are tested only for the record of provider choice. Grants account for £6,033,599.82 and agency staff for £1,285,541.24 [metric:$.population.tags.grant.gbp] [metric:$.population.tags.agency_staff.gbp]; both are tested under R-04, grants because the Rules treat providing a grant to an external organisation as entering a contract [rule:CPR-66].
The Contracts Finder export held 141 council notices, of which 62 were active in the spend window [metric:$.contracts.notices] [metric:$.contracts.active_in_window]. It is a list of published notices, not the council's contract register, which was not available to the planning stage.

## Scope

The register lists 9 rated risks. The auditor recorded 10 decisions by Jeremy Lee dated 2026-10-09: 9 risks are approved and in scope, and 1 is not.

| ID | Risk | Score | Band | Decision | Auditor comment |
|---|---|---|---|---|---|
| R-01 | Quotes not sought for payments just below the quotation thresholds | 6 | Moderate | approve | The revision 1 amendment (R-01 in scope) stands. |
| R-02 | Requirements split into payments that each stay under the quotation threshold | 12 | Medium - High | approve |  |
| R-03 | High-value awards made without Key Decision or the approvals in Appendix A | 10 | Medium - High | approve |  |
| R-04 | Spend above the quotation threshold with no published contract notice | 15 | Extreme | amend | Clause 1.6.2 makes a grant a contract (now CPR-66), so bring grant suppliers with no live notice into R-04, and agency-staff suppliers too, since agency staff is a bought service. Placements stay with R-09. Keep premises (rent, rates, leases) out: these are property costs, not purchases under the Rules; list them under Excluded with that reason. Replace the grants exclusion. Keep the rating unless the evidence moves it. |
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

The programme holds 12 expected controls and 24 test steps, with 289 sampled transactions worth £21,747,431.89, each traceable to its row in the council's published workbooks (see `audit-program.md` and `outputs/samples/`).

## Rules coverage

39 of 66 rules in `rules.json` are cited by a risk, a control or a test. The remaining 27 are not tested in this audit, for these reasons:

- statutory tier: the Threshold parameter is null in rules.json, so the analytics skipped it and no risk was rated on it: CPR-08, CPR-11, CPR-26, CPR-27, CPR-45, CPR-57
- tender handling inside the Procurement Portal (format, late tenders, opening); no tender records in the inputs and no risk rated on it: CPR-12, CPR-13, CPR-14
- contract drafting and terms (written form, standard clauses, data protection, payment terms, indemnities, bonds, insurance); checked on contract files, outside the spend-pattern risks the auditor approved: CPR-31, CPR-33, CPR-34, CPR-35, CPR-36, CPR-37, CPR-38, CPR-39, CPR-41
- custody of the Seal, execution of documents and instruction of Counsel; legal governance with no link to procurement spend: CPR-42, CPR-43, CPR-44, CPR-46, CPR-47, CPR-48
- budget provision and monthly board reporting; governance steps outside the spend data with no risk rated on them: CPR-01, CPR-06
- publication of expenditure over the floor; met by the published workbooks this audit uses as its population. Whether the redaction of payee names is justified is not tested: CPR-03

## Limitations

- The data covers payments over the publication floor only, so split-purchase and duplicate counts are lower bounds [metric:$.tests.split_purchases.parameters.lower_bound_note].
- Payments with a redacted supplier name (2,015 rows, £2,746,746.71) are outside every supplier-level test, so counts and samples do not reach them [metric:$.population.excluded.redacted_supplier.rows] [metric:$.population.excluded.redacted_supplier.gbp].
- Annual figures are annualised estimates: the window total multiplied by 4, with no adjustment for seasonal or one-off spend [metric:$.population.annualisation_factor].
- Contracts Finder holds published notices only; earlier awards, framework call-offs under another buyer, grant agreements not published as notices and exempt placements will not appear, so an unmatched supplier is an indicator to reconcile, not evidence of spend without a contract [metric:$.tests.off_contract.register_present].
- Award values in notices may be estimates or maxima, so a high spend-to-award ratio needs confirming against the signed contract [metric:$.tests.spend_vs_award.parameters.ratio_flag].
- The statutory procurement thresholds are null in the extracted rules, so no test covers the statutory tier; above-threshold tender duties are not tested.
- Net amounts exclude VAT, and the Rules are ambiguous on whether thresholds include it; payments near a threshold may sit on either side of it.
- Waivers, exceptions, award approvals and case notes are not in the published data; those tests depend on records the council provides.
- Direct payments are identifiable in the spend data only through the Adult Social Care narrative 'Direct Payment'. Direct payments for children cannot be identified in the spend data, so T-09.3 samples them from the council's own list, requested in the PBC list; that sample depends on the list being complete.
- Premises costs (rent, rates and leases), £568,884.66 in the window, are outside the tests: the auditor treated them as property costs, not purchases under the Rules [metric:$.population.tags.premises_non_procurement.gbp].

## Review and sign-off

The challenger's points and their status are in `challenges.md`; points marked *for the auditor* need a decision at sign-off. The QA reviewer's checks and verdict are in `review.md`, which ends with the sign-off block.
