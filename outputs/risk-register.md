# Procurement audit planning: risk register

*Status: REVISION 1 for auditor sign-off.*

*Revision 1, following auditor comments dated 2026-10-06 by Jeremy Lee. Changed: R-01 (amended), R-10 (rejected).*

*Generated 2026-10-06 by `build_register.py` from `risk-ratings.json`, `rules.json`, `analytics.json` and `history.json`.*

**Indicators, not findings.** Each risk describes a pattern in public data to investigate. Nothing here asserts wrongdoing by the council, a department, an officer or a supplier.

- Scale: the council's own method from `risk-management-strategy-2024-27.pdf` (likelihood 1 Rare to 5 Certain; impact 1 Negligible to 5 Critical). Score = likelihood × impact. Matrix label from Figure 1; band from Table 4.
- Conflict in the scoring method, not resolved here: Table 4 adds risks scoring 15 or more to the Corporate Risk Register; Figure 4 says 9 or above. Bands use Table 4; the Fig. 4 column marks risks that meet the Figure 4 rule.
- Naming: the Figure 1 matrix uses High where Table 4 names its bands Extreme, Medium - High, Moderate, Low; both are shown.

## Summary

| ID | Risk | L | I | Score | Matrix label | Band (Table 4) | Fig. 4 (≥ 9) | Scope |
|---|---|---|---|---|---|---|---|---|
| R-01 | Quotes not sought for payments just below the quotation thresholds | 2 | 3 | 6 | Moderate | Moderate | no | in |
| R-02 | Requirements split into payments that each stay under the quotation threshold | 3 | 4 | 12 | High | Medium - High | yes | in |
| R-03 | High-value awards made without Key Decision or the approvals in Appendix A | 2 | 5 | 10 | High | Medium - High | yes | in |
| R-04 | Spend above the quotation threshold with no published contract notice | 3 | 5 | 15 | Extreme | Extreme | yes | in |
| R-05 | Duplicate or repeated payments of the same amount | 3 | 3 | 9 | High | Medium - High | yes | in |
| R-06 | Spend continuing after the published contract has ended | 2 | 3 | 6 | Moderate | Moderate | no | in |
| R-07 | Spend running above the awarded contract value without an approved variation | 3 | 4 | 12 | High | Medium - High | yes | in |
| R-08 | Waivers and exceptions granted without the required approval | 2 | 3 | 6 | Moderate | Moderate | no | in |
| R-09 | Care and education placements without the recorded reasons for provider choice | 3 | 4 | 12 | High | Medium - High | yes | in |

## Risks

### R-01: Quotes not sought for payments just below the quotation thresholds

Payments sitting just below a quotation threshold may indicate that the quotes the Rules require were not sought [CPR-53] [CPR-54].

**Likelihood 2 (Unlikely).** Weak signal. Just below the £25,000 threshold there are 46 payments [$.tests.threshold_clustering.per_threshold[1].band_count] against 52 just above it [$.tests.threshold_clustering.per_threshold[1].comparator_count], so there is no excess below the line, and only 10 of them are general procurement [$.tests.threshold_clustering.per_threshold[1].by_tag.general_procurement.rows]. Below £1,000 the band count of 323 [$.tests.threshold_clustering.per_threshold[0].band_count] exceeds the 216 above [$.tests.threshold_clustering.per_threshold[0].comparator_count], but that band includes payments of exactly the threshold value and the rule there asks for a single quote [CPR-53]. No payment falls in the band below the next threshold up [$.tests.threshold_clustering.per_threshold[2].band_count]. Contract Letting received Reasonable Assurance [AUD-01], so no uplift.

**Impact 3 (Medium).** The general-procurement value in the band below the three-quote threshold, £239,427.82 [$.tests.threshold_clustering.per_threshold[1].by_tag.general_procurement.gbp], falls in the Medium financial band [$.scoring_method.impact_scale[2].financial]; the three-quote and contract notice duties are mandatory [CPR-54]. No adjustment.

**Score 6: Moderate (matrix); Moderate (Table 4).**

**Evidence**

- [rule:CPR-53] clause App B row A: "At least one quote must be sought from an appropriate source."
- [rule:CPR-54] clause App B row B1: "Invitations to quote must be sent via the Procurement Portal to at least three appropriate sources, including at least one SME* or VCSE* org…"
- [metric:$.tests.threshold_clustering.per_threshold[1].band_count] 46
- [metric:$.tests.threshold_clustering.per_threshold[1].comparator_count] 52
- [metric:$.tests.threshold_clustering.per_threshold[1].by_tag.general_procurement.rows] 10
- [metric:$.tests.threshold_clustering.per_threshold[1].by_tag.general_procurement.gbp] 239,427.82
- [metric:$.tests.threshold_clustering.per_threshold[0].band_count] 323
- [metric:$.tests.threshold_clustering.per_threshold[0].comparator_count] 216
- [history:AUD-01] Contract Letting: Reasonable Assurance (audit-completed-work-2024-25-annual.pdf, p. 1)

**Proposed focus.** For the general-procurement payments in the band just below the three-quote threshold, check that invitations to quote went to at least three sources through the Procurement Portal and that a contract notice was published.

**Recommended scope: in.** Auditor: "Bring into scope. Threshold-hugging at the £25,000 quote boundary is a standard test and cheap to sample; keep the rating as it is." Sample source: `analytics-full/threshold-clustering.csv`.

### R-02: Requirements split into payments that each stay under the quotation threshold

Repeated payments to one supplier that each stay under a quotation threshold but together cross it may indicate a requirement split to avoid competition [CPR-10].

**Likelihood 3 (Likely).** Clear signal: 42 general-procurement windows (one per supplier) where two or more payments each under £25,000 reach it within 30 days [$.tests.split_purchases.per_threshold[0].headline_general_procurement.windows], well over a handful of suppliers. Held at 3 rather than 4 because regular payments under one existing contract produce the same pattern and the published data cannot tell the two apart. Placement windows (129) are left out because periodic care fees legitimately recur [$.tests.split_purchases.per_threshold[0].care_or_education_placement.windows]. Counts are lower bounds since payments of the publication floor or less are not published [$.tests.split_purchases.parameters.lower_bound_note]. Fraud and financial control are a named source of risk [RT-02]; no adverse audit on the theme, so no uplift.

**Impact 4 (Major).** The flagged general-procurement total of £2,372,829.90 [$.tests.split_purchases.per_threshold[0].headline_general_procurement.gbp] falls in the Critical financial band [$.scoring_method.impact_scale[0].financial]. Reduced by one point: the total is the value of the windows, not a loss, and a split below the quotation threshold matches the Major compliance descriptor, a high possibility of legal challenge [$.scoring_method.impact_scale[1].compliance] [CPR-10].

**Score 12: High (matrix); Medium - High (Table 4).**

**Evidence**

- [rule:CPR-10] clause 6.16: "There shall be no artificial splitting or disaggregation of a contract to avoid the application of the provisions of the Procurement Legisla…"
- [rule:CPR-54] clause App B row B1: "Invitations to quote must be sent via the Procurement Portal to at least three appropriate sources, including at least one SME* or VCSE* org…"
- [metric:$.tests.split_purchases.per_threshold[0].headline_general_procurement.windows] 42
- [metric:$.tests.split_purchases.per_threshold[0].headline_general_procurement.gbp] 2,372,829.90
- [metric:$.tests.split_purchases.per_threshold[0].care_or_education_placement.windows] 129
- [metric:$.tests.split_purchases.parameters.window_days] 30
- [history:RT-02] Finance: financial control, fraud and corruption (source-of-risk prompt) (risk-management-strategy-2024-27.pdf, p. 32)

**Proposed focus.** For a sample of general-procurement windows, establish whether the payments relate to one requirement; where they do, check the competition the combined value required was run, or that an existing contract covers them.

**Recommended scope: in.** Clear signal across many suppliers on a mandatory anti-avoidance rule. Sample source: `analytics-full/split-purchases.csv`.

### R-03: High-value awards made without Key Decision or the approvals in Appendix A

Awards above the Key Decision threshold that do not follow the approval route in Appendix A may indicate contracts awarded outside delegated authority [CPR-02] [CPR-51] [CPR-52].

**Likelihood 2 (Unlikely).** The award approval record is not in the published data, so the control cannot be observed directly. The only data signal is weak: 2 general-procurement windows where payments each under £500,000 reach that value within 30 days [$.tests.split_purchases.per_threshold[1].headline_general_procurement.windows]. No audit in the papers covers award approvals, so no adverse history. The council's compliance appetite names high value transactions [RT-08].

**Impact 5 (Critical).** The flagged windows total £3,509,528.75 [$.tests.split_purchases.per_threshold[1].headline_general_procurement.gbp], in the Critical financial band [$.scoring_method.impact_scale[0].financial]; an award that should have been a Key Decision but was not carries a probable legal challenge [CPR-02]. No adjustment.

**Score 10: High (matrix); Medium - High (Table 4).**

**Evidence**

- [rule:CPR-02] clause 4.3: "Any contract award with a value over £500,000 is a Key Decision of the Council."
- [rule:CPR-50] clause App A row 2: "Relevant Service Director (following recommendation of the S151 officer and Monitoring Officer) shall have delegated authority to award the…"
- [rule:CPR-51] clause App A row 3: "The award of these contracts shall be a Key Decision delegated to the relevant Service Director in consultation with the relevant Portfolio…"
- [rule:CPR-52] clause App A row 4: "Contracts with a value in excess of £2.5million shall require Executive approval, which may be given as below. The Executive shall receive q…"
- [metric:$.tests.split_purchases.per_threshold[1].headline_general_procurement.windows] 2
- [metric:$.tests.split_purchases.per_threshold[1].headline_general_procurement.gbp] 3,509,528.75
- [history:RT-08] Compliance risk appetite: Flexible/Open, includes high value transactions (risk-management-strategy-2024-27.pdf, p. 17)

**Proposed focus.** For the general-procurement windows reaching the Key Decision threshold and the largest annualised suppliers, trace the award to its approval: Key Decision record, board-approved report and the recommendations Appendix A requires.

**Recommended scope: in.** Small population with Critical exposure; the approval route is the control the data cannot see. Sample source: `analytics-full/split-purchases.csv`.

### R-04: Spend above the quotation threshold with no published contract notice

Suppliers paid at or above the quotation threshold on an annualised basis with no matching published contract notice may indicate spend without the competition or notice the Rules require [CPR-54]. The notice export is not a contract register, so this is an indicator to check, not evidence of off-contract spend.

**Likelihood 3 (Likely).** 185 general-procurement suppliers at or above £25,000 annualised have no exact-name match to an active notice [$.tests.off_contract.unmatched_general_procurement.suppliers], against 40 exact matches across all tags [$.tests.off_contract.per_match_class.exact.suppliers]: a clear signal by count. Held at 3 because the source holds published notices only and no contract register was available [$.tests.off_contract.register_present]; earlier awards, notices placed elsewhere, framework call-offs under another buyer and exempt placements will not appear. Placement suppliers are left out because placements are exempt from competition [CPR-64]. Contract Letting received Reasonable Assurance [AUD-01], so no uplift.

**Impact 5 (Critical).** The annualised estimate for unmatched general-procurement suppliers, £98,484,571.20 [$.tests.off_contract.unmatched_general_procurement.annualised_estimate_gbp], is in the Critical financial band [$.scoring_method.impact_scale[0].financial]; competition and publication duties apply [CPR-54] [CPR-05]. No adjustment.

**Score 15: Extreme (matrix); Extreme (Table 4).**

**Evidence**

- [rule:CPR-54] clause App B row B1: "Invitations to quote must be sent via the Procurement Portal to at least three appropriate sources, including at least one SME* or VCSE* org…"
- [rule:CPR-05] clause 5.2.1: "A register of contracts, including those in progress and those awarded, with key information such as the contract value, duration and suppli…"
- [rule:CPR-64] clause App C row F: "Service Directors must ensure that a record of the reasons for the choice of provider is maintained on the individual’s case notes."
- [metric:$.tests.off_contract.unmatched_general_procurement.suppliers] 185
- [metric:$.tests.off_contract.unmatched_general_procurement.annualised_estimate_gbp] 98,484,571.20
- [metric:$.tests.off_contract.per_match_class.exact.suppliers] 40
- [metric:$.tests.off_contract.register_present] False
- [history:AUD-01] Contract Letting: Reasonable Assurance (audit-completed-work-2024-25-annual.pdf, p. 1)

**Proposed focus.** Obtain the council's contract register and reconcile it to the unmatched general-procurement suppliers, confirming near matches first; for suppliers still unmatched, request the quote, tender or waiver record behind the spend.

**Recommended scope: in.** Largest exposure in the register; the reconciliation also tests register completeness (R-10). Sample source: `analytics-full/off-contract.csv`.

### R-05: Duplicate or repeated payments of the same amount

Payments to the same supplier for the same amount within seven days may indicate duplicate or repeated payment without separate evidence of purchase [CPR-29].

**Likelihood 3 (Likely).** Clear signal in general procurement: 33 groups share an identical payment date [$.tests.duplicates.tiers.same_timestamp.by_tag.general_procurement.groups] and 35 more fall on different dates within seven days [$.tests.duplicates.tiers.different_time.by_tag.general_procurement.groups]. Placement groups (395 same-date, 204 different-date) [$.tests.duplicates.tiers.same_timestamp.by_tag.care_or_education_placement.groups] are not counted towards the score because fees at a standard rate legitimately repeat across service users. Accounts Payable received Reasonable Assurance [AUD-15], so no uplift.

**Impact 3 (Medium).** The general-procurement value beyond the first payment in the different-date tier, £299,374.24 [$.tests.duplicates.tiers.different_time.by_tag.general_procurement.gbp_beyond_first], is in the Medium financial band [$.scoring_method.impact_scale[2].financial]; the same-date tier adds a smaller £60,213.42 [$.tests.duplicates.tiers.same_timestamp.by_tag.general_procurement.gbp_beyond_first]. This is within the council's stated financial appetite range [RT-07]. No adjustment.

**Score 9: High (matrix); Medium - High (Table 4).**

**Evidence**

- [rule:CPR-29] clause 10.1: "There should be written evidence of all purchases (which shall include electronic evidence)."
- [metric:$.tests.duplicates.tiers.same_timestamp.by_tag.general_procurement.groups] 33
- [metric:$.tests.duplicates.tiers.different_time.by_tag.general_procurement.groups] 35
- [metric:$.tests.duplicates.tiers.different_time.by_tag.general_procurement.gbp_beyond_first] 299,374.24
- [metric:$.tests.duplicates.tiers.same_timestamp.by_tag.care_or_education_placement.groups] 395
- [history:AUD-15] Accounts Payable: Reasonable Assurance (audit-completed-work-2025-26-q3.pdf, p. 1)
- [history:RT-07] Financial risk appetite: Flexible, £250k-£500k (risk-management-strategy-2024-27.pdf, p. 17)

**Proposed focus.** For a sample of general-procurement groups, match each payment to a distinct invoice and purchase record, and confirm any true duplicate was recovered; include a few of the largest placement groups to confirm they relate to different service users.

**Recommended scope: in.** Clear signal with a direct test against invoices. Sample source: `analytics-full/duplicates.csv`.

### R-06: Spend continuing after the published contract has ended

Payments to suppliers whose only published contract notices ended before the spend window may indicate spend continuing after expiry without an approved extension [CPR-61].

**Likelihood 2 (Unlikely).** Weak signal: 7 suppliers [$.tests.expired_notice_spend.suppliers], and a newer contract may exist with no notice [$.tests.expired_notice_spend.caveat]. Contract management is a named source of risk [RT-03]; no adverse audit on the theme, so no uplift.

**Impact 3 (Medium).** The annualised estimate of £761,467.68 [$.tests.expired_notice_spend.annualised_estimate_gbp] falls in the Major financial band [$.scoring_method.impact_scale[1].financial]. Reduced by one point: a missing extension approval matches the Medium compliance descriptor, a reasonable possibility of legal challenge [$.scoring_method.impact_scale[2].compliance] [CPR-61]; the window total of £190,366.92 [$.tests.expired_notice_spend.gbp] includes one-off payments that annualising overstates.

**Score 6: Moderate (matrix); Moderate (Table 4).**

**Evidence**

- [rule:CPR-61] clause App C row D: "Approval of the S151 Officer"
- [metric:$.tests.expired_notice_spend.suppliers] 7
- [metric:$.tests.expired_notice_spend.gbp] 190,366.92
- [metric:$.tests.expired_notice_spend.annualised_estimate_gbp] 761,467.68
- [history:RT-03] Contracts and partnerships: contractor failure, procurement contract management (risk-management-strategy-2024-27.pdf, p. 33)

**Proposed focus.** For each flagged supplier, obtain the current contract or the S151-approved extension covering the payments in the window.

**Recommended scope: in.** Small, fully testable population. Sample source: `analytics-full/expired-notice-spend.csv`.

### R-07: Spend running above the awarded contract value without an approved variation

Annualised spend well above a contract's awarded annual rate may indicate a variation of scope or value without the approval the Rules require [CPR-62] [CPR-63].

**Likelihood 3 (Likely).** Clear signal: 12 of 23 assessed suppliers have an annualised estimate at least 1.25 times the award's annual rate [$.tests.spend_vs_award.flagged] [$.tests.spend_vs_award.suppliers_assessed], more than a handful. Award values may be estimates or maxima [$.tests.spend_vs_award.caveat]. Contract management is a named source of risk [RT-03]; no adverse audit on the theme, so no uplift.

**Impact 4 (Major).** The flagged annualised estimate of £5,353,417.28 [$.tests.spend_vs_award.flagged_annualised_estimate_gbp] is in the Critical financial band [$.scoring_method.impact_scale[0].financial]. Reduced by one point: the exposure is the excess over each award, which is smaller than the flagged total, and an unapproved variation matches the Major compliance descriptor [$.scoring_method.impact_scale[1].compliance] [CPR-63].

**Score 12: High (matrix); Medium - High (Table 4).**

**Evidence**

- [rule:CPR-62] clause App C row E: "For contract value below the Threshold prior written approval from the Monitoring Officer and S151 Officer is required."
- [rule:CPR-63] clause App C row E: "For contract value greater than the Threshold, approval of the relevant board, following the submission of an extension report to the releva…"
- [metric:$.tests.spend_vs_award.flagged] 12
- [metric:$.tests.spend_vs_award.suppliers_assessed] 23
- [metric:$.tests.spend_vs_award.flagged_annualised_estimate_gbp] 5,353,417.28
- [metric:$.tests.spend_vs_award.parameters.ratio_flag] 1.25
- [history:RT-03] Contracts and partnerships: contractor failure, procurement contract management (risk-management-strategy-2024-27.pdf, p. 33)

**Proposed focus.** For each flagged supplier, compare spend to the signed contract value and obtain any variation approval; confirm whether the published award value was an estimate or a maximum.

**Recommended scope: in.** Clear signal across a defined population of matched contracts. Sample source: `analytics-full/spend-vs-award.csv`.

### R-08: Waivers and exceptions granted without the required approval

Competition may be waived or an exception applied without the documentation and approval the Rules require; the Rules name different approvers for a waiver [CPR-17] [CPR-18].

**Likelihood 2 (Unlikely).** The waiver and exception record is not in the published data, so the control cannot be observed; no audit in the papers covers waivers, so no adverse history and no uplift. The Rules conflict on who may waive: the relevant Executive Director or Chief Executive under one clause [CPR-17], only the Monitoring Officer or S151 Officer under another [CPR-18], which makes a wrongly authorised waiver harder to spot.

**Impact 3 (Medium).** No exposure in pounds can be measured for waivers. Rated on the compliance descriptor: a waiver approved by the wrong officer or left undocumented gives a reasonable possibility of successful legal challenge, the Medium descriptor [$.scoring_method.impact_scale[2].compliance]; every waiver must be documented and approved by the S151 Officer [CPR-22] [CPR-24].

**Score 6: Moderate (matrix); Moderate (Table 4).**

**Evidence**

- [rule:CPR-17] clause 7.2.2: "at the discretion of the relevant Executive Director and/or the Chief Executive, acting lawfully, who may proceed in a manner most expedient…"
- [rule:CPR-18] clause 7.3: "Only the Monitoring Officer and/or the S.151 Officer may grant a waiver or an exception to these Rules, subject to exception values and dele…"
- [rule:CPR-22] clause 7.5.1: "All exceptions or waivers to these Rules must: 7.5.1 be fully documented;"
- [rule:CPR-23] clause 7.5.2: "for any contract where the requirement to hold a competitive process is not excluded by the Procurement Legislation, be subject to a written…"
- [rule:CPR-24] clause 7.5.3: "be subject to approval by the S.151 Officer who shall record they have considered the reasons for the waiver and that they are satisfied tha…"

**Proposed focus.** Obtain the waiver and exception log for the window, check each entry for documentation, advance approval by the correct officer and a board report where required, and ask which approver the council treats as authoritative.

**Recommended scope: in.** Mandatory control the data cannot see, with conflicting approver wording in the Rules.

### R-09: Care and education placements without the recorded reasons for provider choice

Care and education placements, which are exempt from competition, may be made without the reasons for the choice of provider recorded on the case notes as the Rules require [CPR-64].

**Likelihood 3 (Likely).** Case notes are not in the spend data, so the control cannot be observed: base score 2. The 303 placement suppliers paid at or above the quotation threshold with no notice [$.tests.off_contract.unmatched_by_dominant_tag.care_or_education_placement.suppliers] are expected under the exemption and are not read as a signal. Purchase of Residential and Nursing Care received Reasonable Assurance [AUD-18]. Raised to 3 by the repeat-finding uplift below.

**Repeat-finding uplift (+1 included above).** Personal Budgets (Direct Payments) received Limited Assurance in the latest completed-work appendix [AUD-16]; direct payments fall within this theme of care purchased outside the Rules, so likelihood is raised by one point.

**Impact 4 (Major).** Placement spend in the window, £30,571,711.30 [$.population.tags.care_or_education_placement.gbp], is in the Critical financial band [$.scoring_method.impact_scale[0].financial]. Reduced by one point: the duty at stake is a recording requirement under an exemption, nearer the Major compliance descriptor than probable regulatory intervention [$.scoring_method.impact_scale[1].compliance] [CPR-64].

**Score 12: High (matrix); Medium - High (Table 4).**

**Evidence**

- [rule:CPR-64] clause App C row F: "Service Directors must ensure that a record of the reasons for the choice of provider is maintained on the individual’s case notes."
- [rule:CPR-59] clause App C row B: "Key decisions must be recorded and the relevant process under PSR followed"
- [metric:$.population.tags.care_or_education_placement.gbp] 30,571,711.30
- [metric:$.tests.off_contract.unmatched_by_dominant_tag.care_or_education_placement.suppliers] 303
- [history:AUD-16] Personal Budgets (Direct Payments): Limited Assurance (audit-completed-work-2025-26-q3.pdf, p. 1)
- [history:AUD-18] Purchase of Residential and Nursing Care Provision: Reasonable Assurance (audit-completed-work-2025-26-q3.pdf, p. 1)

**Proposed focus.** For a sample of placement payments, check that the case notes record the reasons for the provider chosen and, where the Provider Selection Regime applies, that its process was followed.

**Recommended scope: in.** Adverse audit on the theme and the largest tagged spend population. Sample source: `analytics-full/spend-clean.csv`.

## Excluded

- Tender and advertising duties above the statutory threshold: The three statutory threshold values are null in rules.json, so analytics.json skipped the statutory tier of every test; not rated until the auditor supplies the figures with a source.
- Grants treated as contracts: Grant spend is tagged separately, and the clause that would bring a grant within the Rules is a definition excluded from rules.json with no rule ID to cite.
- R-10: Contract register incomplete or awards not notified to it: Auditor: Covered by R-04: reconciling unmatched suppliers to the contract register already tests its completeness.

## Auditor decisions

Decisions by Jeremy Lee, dated 2026-10-06.

| ID | Decision | Applied as | Comment |
|---|---|---|---|
| R-01 | amend | amended | Bring into scope. Threshold-hugging at the £25,000 quote boundary is a standard test and cheap to sample; keep the rating as it is. |
| R-02 | approve | kept as rated |  |
| R-03 | approve | kept as rated |  |
| R-04 | approve | kept as rated |  |
| R-05 | approve | kept as rated |  |
| R-06 | approve | kept as rated |  |
| R-07 | approve | kept as rated |  |
| R-08 | approve | kept as rated |  |
| R-09 | approve | kept as rated |  |
| R-10 | reject | rejected; moved to excluded | Covered by R-04: reconciling unmatched suppliers to the contract register already tests its completeness. |
