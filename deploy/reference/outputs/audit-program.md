# Audit program

*Generated 2026-10-06 by `build_pack.py` from `audit-plan.json`, `risk-register.md` (revision 1), `auditor-comments.md` by Jeremy Lee dated 2026-10-06, `rules.json` and `analytics.json`. Status: DRAFT for challenge, QA review and auditor sign-off.*

**Indicators, not findings.** Every test below checks a control against a pattern in public data. Nothing here asserts wrongdoing by the council, a department, an officer or a supplier.

9 risks in scope, 11 controls, 17 tests, 229 sampled transactions. Samples are drawn by the builder from `analytics-full/` by the recipe stated under each test, and every transaction is listed with its workbook row.


## R-01: Quotes not sought for payments just below the quotation thresholds [6 (Moderate; Moderate)]

**Audit objective.** Conclude whether general-procurement payments just below the three-quote threshold were bought under the quotation route their full requirement value required.

**C-01.1. Expected control.** The value of the whole requirement is estimated before the route is chosen; one quote is sought below the three-quote threshold and, at or above it, invitations go through the Procurement Portal to at least three sources with a contract notice published. [CPR-53, CPR-54, CPR-07] Owner: Relevant Service Director.

**T-01.1. Test.** For each sampled payment, obtain the order and the requirement it relates to and confirm the estimated value of the whole requirement. Where that value is below the three-quote threshold, confirm at least one quote was sought. Where it is at or above it, confirm invitations went through the Procurement Portal to at least three sources, the quotes were evaluated against criteria notified in advance, and a contract notice was published. A pass is a documented route that matches the requirement value. Also confirm the award was made by the relevant Service Director or an officer nominated in writing. Every general-procurement payment in the band is tested except payments to public bodies, which are excluded by the analytics' inter-authority payee pattern because they are not competed purchases. [CPR-53, CPR-54, CPR-15, CPR-28, CPR-49, metric:$.tests.threshold_clustering.per_threshold[1].by_tag.general_procurement.rows]  
**Evidence to inspect:** Purchase order, requirement estimate, Procurement Portal invitation record, quotations received, evaluation record, contract notice  
**Sample:** 9 items from `threshold-clustering.csv`, where threshold = 25000, tag = general_procurement, largest Net amount first, excluding Supplier name matching /\b(?:COUNCIL|BOROUGH|COUNTY|CNCL|NHS|POLICE|FIRE AUTHORITY|FIRE AND RESCUE|HMRC|HM REVENUE|DEPARTMENT FOR|MINISTRY OF)\b/, (only 9 available); 9 transactions

| # | Row ID | Date | Supplier | Amount | Service |
|---|---|---|---|---|---|
| 1 | `Over500_2026_P04_-_published.xlsx:1281` | 2026-07-29 | The Better Group Ltd | £24,476.02 | Adult Social Care |
| 2 | `Over500_2026_P03_-_published.xlsx:649` | 2026-06-18 | Triple Value Impact | £24,244.00 | Chief Executive |
| 3 | `Over500_2026_P02_-_published.xlsx:560` | 2026-05-12 | DevComms South East Ltd | £24,227.07 | Development & Housing |
| 4 | `Over500_2026_P03_-_published.xlsx:13` | 2026-06-01 | The Better Group Ltd | £24,088.98 | Children's Social Care |
| 5 | `Over500_2026_P03_-_published.xlsx:396` | 2026-06-10 | BookingLab Limited | £24,000.00 | Transformation, Customer & ICT |
| 6 | `Over500_2026_P02_-_published.xlsx:530` | 2026-05-27 | Elior UK PLC | £23,694.03 | Adult Social Care |
| 7 | `Over500_2026_P03_-_published.xlsx:683` | 2026-06-08 | VolkerHighways Ltd | £23,591.22 | Environment |
| 8 | `Over500_2026_P03_-_published.xlsx:440` | 2026-06-16 | Elior UK PLC | £23,516.69 | Adult Social Care |
| 9 | `Over500_2026_P04_-_published.xlsx:533` | 2026-07-28 | Elior UK PLC | £23,173.08 | Adult Social Care |


## R-02: Requirements split into payments that each stay under the quotation threshold [12 (High; Medium - High)]

**Audit objective.** Conclude whether repeated general-procurement payments to one supplier that together reach the three-quote threshold were one requirement bought without the competition its combined value required.

**C-02.1. Expected control.** Requirements are aggregated before the procurement route is chosen, so that no contract is split or disaggregated to stay under a threshold. [CPR-10, CPR-54, CPR-55] Owner: Relevant Service Director.

**T-02.1. Test.** For each sampled window whose combined total sits just over the three-quote threshold, the pattern a split shows most plainly, obtain the orders and invoices behind the sampled payments, and the list of all payments in the window from the ledger, and establish whether they relate to one requirement. Where they do, confirm the competition the combined value required was run, or that an existing contract or a purchasing scheme the council had advice to use covers them. Where they do not, record the separate requirements. A pass is either separate requirements or one requirement bought under the correct route. [CPR-10, CPR-54, CPR-25, metric:$.tests.split_purchases.per_threshold[0].headline_general_procurement.windows]  
**Evidence to inspect:** Purchase orders, invoices, quotations or tender record, contract or framework call-off, purchasing scheme advice  
**Sample:** 5 items from `split-purchases.csv`, where threshold = 25000, tag = general_procurement, total_gbp ≥ 25000, total_gbp ≤ 50000, largest total_gbp first, largest 5 payments per item; 24 transactions

| # | Row ID | Date | Supplier | Amount | Service |
|---|---|---|---|---|---|
| 1 | `Over500_2026_P04_-_published.xlsx:227` | 2026-07-22 | COMPASS EXECUTIVE CARS (UK) LTD | £4,455.00 | Education & SEND |
| 1 | `Over500_2026_P04_-_published.xlsx:478` | 2026-07-21 | COMPASS EXECUTIVE CARS (UK) LTD | £3,885.00 | Education & SEND |
| 1 | `Over500_2026_P04_-_published.xlsx:235` | 2026-07-15 | COMPASS EXECUTIVE CARS (UK) LTD | £3,654.00 | Education & SEND |
| 1 | `Over500_2026_P04_-_published.xlsx:429` | 2026-07-15 | COMPASS EXECUTIVE CARS (UK) LTD | £3,264.50 | Adult Social Care |
| 1 | `Over500_2026_P04_-_published.xlsx:288` | 2026-07-30 | COMPASS EXECUTIVE CARS (UK) LTD | £3,135.00 | Education & SEND |
| 2 | `Over500_2026_P03_-_published.xlsx:208` | 2026-06-03 | Sikandar Hayat t/a Prompt Cars | £17,607.50 | Education & SEND |
| 2 | `Over500_2026_P03_-_published.xlsx:162` | 2026-06-03 | Sikandar Hayat t/a Prompt Cars | £9,944.00 | Education & SEND |
| 2 | `Over500_2026_P03_-_published.xlsx:254` | 2026-06-04 | Sikandar Hayat t/a Prompt Cars | £2,520.00 | Education & SEND |
| 2 | `Over500_2026_P03_-_published.xlsx:239` | 2026-06-04 | Sikandar Hayat t/a Prompt Cars | £2,173.50 | Education & SEND |
| 2 | `Over500_2026_P03_-_published.xlsx:157` | 2026-06-03 | Sikandar Hayat t/a Prompt Cars | £2,111.00 | Children's Social Care |
| 3 | `Over500_2026_P02_-_published.xlsx:747` | 2026-05-18 | SUMMIT CONTRACTORS BUILD LTD | £18,425.00 | Development & Housing |
| 3 | `Over500_2026_P03_-_published.xlsx:735` | 2026-06-08 | SUMMIT CONTRACTORS BUILD LTD | £16,128.59 | Development & Housing |
| 3 | `Over500_2026_P03_-_published.xlsx:736` | 2026-06-11 | SUMMIT CONTRACTORS BUILD LTD | £6,817.50 | Development & Housing |
| 3 | `Over500_2026_P03_-_published.xlsx:712` | 2026-06-16 | SUMMIT CONTRACTORS BUILD LTD | £5,197.46 | Development & Housing |
| 4 | `Over500_2026_P02_-_published.xlsx:677` | 2026-05-01 | Bolinda UK Ltd | £12,000.00 | Community Services |
| 4 | `Over500_2026_P02_-_published.xlsx:679` | 2026-05-05 | Bolinda UK Ltd | £10,500.00 | Community Services |
| 4 | `Over500_2026_P02_-_published.xlsx:678` | 2026-05-01 | Bolinda UK Ltd | £8,000.00 | Community Services |
| 4 | `Over500_2026_P02_-_published.xlsx:648` | 2026-05-21 | Bolinda UK Ltd | £7,500.00 | Community Services |
| 4 | `Over500_2026_P02_-_published.xlsx:680` | 2026-05-05 | Bolinda UK Ltd | £7,000.00 | Community Services |
| 5 | `Over500_2026_P04_-_published.xlsx:148` | 2026-07-01 | Glen Cleaning Company Ltd | £5,829.96 | Finance, Property & Procurement |
| 5 | `Over500_2026_P04_-_published.xlsx:399` | 2026-07-24 | Glen Cleaning Company Ltd | £5,829.96 | Finance, Property & Procurement |
| 5 | `Over500_2026_P03_-_published.xlsx:307` | 2026-06-30 | Glen Cleaning Company Ltd | £2,543.28 | Adult Social Care |
| 5 | `Over500_2026_P04_-_published.xlsx:127` | 2026-07-20 | Glen Cleaning Company Ltd | £2,439.00 | Adult Social Care |
| 5 | `Over500_2026_P03_-_published.xlsx:132` | 2026-06-30 | Glen Cleaning Company Ltd | £1,911.14 | Community Services |

**T-02.2. Test.** For each of the largest remaining windows, obtain the orders and invoices behind the sampled payments, and the list of all payments in the window from the ledger, and establish whether they relate to one requirement. Where they do, confirm the competition the combined value required was run, or that an existing contract or a purchasing scheme the council had advice to use covers them. Where they do not, record the separate requirements. A pass is either separate requirements or one requirement bought under the correct route. [CPR-10, CPR-54, CPR-25, metric:$.tests.split_purchases.per_threshold[0].headline_general_procurement.windows]  
**Evidence to inspect:** Purchase orders, invoices, quotations or tender record, contract or framework call-off, purchasing scheme advice  
**Sample:** 5 items from `split-purchases.csv`, where threshold = 25000, tag = general_procurement, largest total_gbp first, largest 5 payments per item, excluding suppliers and rows already drawn in T-02.1; 25 transactions

| # | Row ID | Date | Supplier | Amount | Service |
|---|---|---|---|---|---|
| 1 | `Over500_2026_P02_-_published.xlsx:2185` | 2026-05-20 | VolkerHighways Ltd | £19,420.72 | Environment |
| 1 | `Over500_2026_P02_-_published.xlsx:723` | 2026-05-05 | VolkerHighways Ltd | £18,033.36 | Environment |
| 1 | `Over500_2026_P02_-_published.xlsx:701` | 2026-05-12 | VolkerHighways Ltd | £17,896.87 | Environment |
| 1 | `Over500_2026_P02_-_published.xlsx:2179` | 2026-05-19 | VolkerHighways Ltd | £17,882.35 | Environment |
| 1 | `Over500_2026_P02_-_published.xlsx:2178` | 2026-05-05 | VolkerHighways Ltd | £16,916.01 | Environment |
| 2 | `Over500_2026_P03_-_published.xlsx:13` | 2026-06-01 | The Better Group Ltd | £24,088.98 | Children's Social Care |
| 2 | `Over500_2026_P03_-_published.xlsx:2397` | 2026-06-01 | The Better Group Ltd | £22,361.26 | Adult Social Care |
| 2 | `Over500_2026_P02_-_published.xlsx:9` | 2026-05-28 | The Better Group Ltd | £20,457.43 | Adult Social Care |
| 2 | `Over500_2026_P02_-_published.xlsx:10` | 2026-05-28 | The Better Group Ltd | £19,605.14 | Children's Social Care |
| 2 | `Over500_2026_P03_-_published.xlsx:2396` | 2026-06-01 | The Better Group Ltd | £18,039.18 | Adult Social Care |
| 3 | `Over500_2026_P03_-_published.xlsx:269` | 2026-06-12 | Newbury & District Ltd | £14,852.00 | Environment |
| 3 | `Over500_2026_P03_-_published.xlsx:268` | 2026-06-01 | Newbury & District Ltd | £13,826.61 | Environment |
| 3 | `Over500_2026_P03_-_published.xlsx:274` | 2026-06-30 | Newbury & District Ltd | £13,663.85 | Environment |
| 3 | `Over500_2026_P03_-_published.xlsx:171` | 2026-06-02 | Newbury & District Ltd | £10,529.33 | Education & SEND |
| 3 | `Over500_2026_P03_-_published.xlsx:336` | 2026-06-02 | Newbury & District Ltd | £9,861.00 | Education & SEND |
| 4 | `Over500_2026_P04_-_published.xlsx:450` | 2026-07-08 | WEAVAWAY TRAVEL LTD | £9,615.23 | Education & SEND |
| 4 | `Over500_2026_P04_-_published.xlsx:452` | 2026-07-08 | WEAVAWAY TRAVEL LTD | £9,483.38 | Education & SEND |
| 4 | `Over500_2026_P04_-_published.xlsx:183` | 2026-07-08 | WEAVAWAY TRAVEL LTD | £8,226.54 | Education & SEND |
| 4 | `Over500_2026_P04_-_published.xlsx:456` | 2026-07-24 | WEAVAWAY TRAVEL LTD | £8,097.04 | Education & SEND |
| 4 | `Over500_2026_P04_-_published.xlsx:305` | 2026-07-24 | WEAVAWAY TRAVEL LTD | £7,986.00 | Education & SEND |
| 5 | `Over500_2026_P04_-_published.xlsx:735` | 2026-07-13 | Roadside Technologies Ltd | £21,000.00 | Environment |
| 5 | `Over500_2026_P04_-_published.xlsx:733` | 2026-07-13 | Roadside Technologies Ltd | £11,188.22 | Environment |
| 5 | `Over500_2026_P04_-_published.xlsx:1287` | 2026-07-13 | Roadside Technologies Ltd | £10,298.22 | Environment |
| 5 | `Over500_2026_P04_-_published.xlsx:601` | 2026-07-13 | Roadside Technologies Ltd | £9,103.64 | Environment |
| 5 | `Over500_2026_P04_-_published.xlsx:740` | 2026-07-13 | Roadside Technologies Ltd | £9,103.64 | Environment |


## R-03: High-value awards made without Key Decision or the approvals in Appendix A [10 (High; Medium - High)]

**Audit objective.** Conclude whether high-value awards followed the approval route in Appendix A, including Key Decision status above the Key Decision threshold.

**C-03.1. Expected control.** Awards above the Key Decision threshold are treated as Key Decisions and follow the Appendix A route for their value band: S151 Officer and Monitoring Officer recommendation, a board-approved written report and, at the top band, Executive approval. [CPR-02, CPR-50, CPR-51, CPR-52] Owner: Relevant Service Director.

**T-03.1. Test.** For each general-procurement window where payments each under the Key Decision threshold together reach it, obtain the contract the sampled payments, and the rest of the window, relate to and its award approval. Confirm the award value, whether it was recorded as a Key Decision, and that the Appendix A approvals for its value band are on file before award. [CPR-02, CPR-51, metric:$.tests.split_purchases.per_threshold[1].headline_general_procurement.windows]  
**Evidence to inspect:** Contract, award report, Key Decision record and Forward Plan entry, S151 and Monitoring Officer recommendations, board approval  
**Sample:** 2 items from `split-purchases.csv`, where threshold = 500000, tag = general_procurement, largest total_gbp first, largest 5 payments per item, (only 2 available); 9 transactions

| # | Row ID | Date | Supplier | Amount | Service |
|---|---|---|---|---|---|
| 1 | `Over500_2026_P03_-_published.xlsx:699` | 2026-06-08 | VolkerHighways Ltd | £329,988.88 | Environment |
| 1 | `Over500_2026_P03_-_published.xlsx:701` | 2026-06-09 | VolkerHighways Ltd | £307,338.45 | Environment |
| 1 | `Over500_2026_P03_-_published.xlsx:729` | 2026-06-08 | VolkerHighways Ltd | £299,416.56 | Environment |
| 1 | `Over500_2026_P02_-_published.xlsx:711` | 2026-05-26 | VolkerHighways Ltd | £200,305.25 | Environment |
| 1 | `Over500_2026_P02_-_published.xlsx:702` | 2026-05-13 | VolkerHighways Ltd | £195,844.36 | Environment |
| 2 | `Over500_2026_P02_-_published.xlsx:473` | 2026-05-27 | SoftwareONE UK Ltd | £375,697.68 | Transformation, Customer & ICT |
| 2 | `Over500_2026_P02_-_published.xlsx:474` | 2026-05-27 | SoftwareONE UK Ltd | £85,871.04 | Transformation, Customer & ICT |
| 2 | `Over500_2026_P02_-_published.xlsx:653` | 2026-05-27 | SoftwareONE UK Ltd | £59,650.56 | Transformation, Customer & ICT |
| 2 | `Over500_2026_P02_-_published.xlsx:654` | 2026-05-27 | SoftwareONE UK Ltd | £1,759.34 | Transformation, Customer & ICT |

**T-03.2. Test.** For the general-procurement suppliers matched to a published notice whose annualised estimate is at or above the Key Decision threshold, trace the award in the notice to its approval: Key Decision record where the award value requires one, the board-approved written report and the recommendations Appendix A requires. Confirm the approvals predate the award date. [CPR-50, CPR-51, CPR-52, metric:$.tests.off_contract.per_match_class.exact.suppliers]  
**Evidence to inspect:** Contract award notice, award report, Key Decision record, board minutes, Executive approval where the value requires it  
**Sample:** 7 items from `off-contract.csv`, where match_class = exact, dominant_tag = general_procurement, annualised estimate ≥ 500000, largest annualised estimate first, 2 payments per supplier, (only 7 available); 13 transactions

| # | Row ID | Date | Supplier | Amount | Service |
|---|---|---|---|---|---|
| 1 | `Over500_2026_P02_-_published.xlsx:437` | 2026-05-20 | Newbury & District Ltd | £60,797.19 | Environment |
| 1 | `Over500_2026_P03_-_published.xlsx:267` | 2026-06-01 | Newbury & District Ltd | £59,626.76 | Environment |
| 2 | `Over500_2026_P02_-_published.xlsx:669` | 2026-05-26 | ASCIA CONSTRUCTION LIMITED | £332,579.29 | Education & SEND |
| 3 | `Over500_2026_P04_-_published.xlsx:905` | 2026-07-22 | NEC SOFTWARE SOLUTIONS UK LIMITED | £129,125.00 | Finance, Property & Procurement |
| 3 | `Over500_2026_P04_-_published.xlsx:492` | 2026-07-22 | NEC SOFTWARE SOLUTIONS UK LIMITED | £91,629.15 | Finance, Property & Procurement |
| 4 | `Over500_2026_P03_-_published.xlsx:2130` | 2026-06-09 | TWO SAINTS LTD | £38,775.00 | Development & Housing |
| 4 | `Over500_2026_P04_-_published.xlsx:3181` | 2026-07-22 | TWO SAINTS LTD | £38,775.00 | Development & Housing |
| 5 | `Over500_2026_P04_-_published.xlsx:450` | 2026-07-08 | WEAVAWAY TRAVEL LTD | £9,615.23 | Education & SEND |
| 5 | `Over500_2026_P04_-_published.xlsx:452` | 2026-07-08 | WEAVAWAY TRAVEL LTD | £9,483.38 | Education & SEND |
| 6 | `Over500_2026_P04_-_published.xlsx:321` | 2026-07-14 | FD TRAVELS LIMITED T/A SCHOOL EXPRESS | £4,074.00 | Education & SEND |
| 6 | `Over500_2026_P04_-_published.xlsx:266` | 2026-07-14 | FD TRAVELS LIMITED T/A SCHOOL EXPRESS | £4,018.00 | Education & SEND |
| 7 | `Over500_2026_P04_-_published.xlsx:260` | 2026-07-13 | BROADWAY CARS | £5,487.69 | Education & SEND |
| 7 | `Over500_2026_P04_-_published.xlsx:259` | 2026-07-13 | BROADWAY CARS | £5,330.00 | Education & SEND |


## R-04: Spend above the quotation threshold with no published contract notice [15 (Extreme; Extreme)]

**Audit objective.** Conclude whether general-procurement suppliers paid at or above the three-quote threshold on an annualised basis are covered by a recorded contract that was competed and published as the Rules require.

**C-04.1. Expected control.** Every award is notified to the Service Lead for Commissioning and Procurement and recorded on the council's contract register, which is published with value, duration and supplier. [CPR-05, CPR-32] Owner: Service Lead for Commissioning and Procurement.

**T-04.1. Test.** Obtain the council's contract register as at the end of the spend window and reconcile it to the full list of unmatched general-procurement suppliers in the flagged list, confirming the near-name matches first. Record each supplier as covered by a register entry, covered by a framework or another buyer's contract, or not on the register. A pass is a register entry for each supplier with live spend. [CPR-05, CPR-32, metric:$.tests.off_contract.unmatched_general_procurement.suppliers, metric:$.matching.near_contain]  
**Evidence to inspect:** Contract register extract, near-match list, framework access agreements  
**Sample:** population reconciliation of every unmatched general-procurement supplier in off-contract.csv against the council's contract register, near matches first; no transaction sample

**C-04.2. Expected control.** Spend at or above the three-quote threshold is let through the Procurement Portal with the quotes or tenders its value requires, a published notice approved by the Service Lead, or a recorded framework call-off or approved waiver. [CPR-54, CPR-55, CPR-56, CPR-04, CPR-07, CPR-09, CPR-60] Owner: Relevant Service Director.

**T-04.2. Test.** For each sampled supplier, obtain the record behind the spend: the quotation or tender run through the Procurement Portal with its evaluation against notified criteria and its published notice, or the framework call-off with Monitoring Officer approval, or the approved waiver. Confirm the award was made by the officer Appendix A names for its value: the relevant Service Director or a nominated officer below the Threshold, and the Appendix A approval where the value passes the Key Decision threshold. A pass is a record whose route matches the annualised value. A sampled supplier that T-04.1 finds on the contract register is replaced by the next supplier in the same recipe order. Payees matching the analytics' inter-authority pattern are excluded because payments to public bodies are not competed purchases. [CPR-54, CPR-15, CPR-16, CPR-60, CPR-49, CPR-51, metric:$.tests.off_contract.unmatched_general_procurement.annualised_estimate_gbp]  
**Evidence to inspect:** Portal quotation or tender record, evaluation and award decision, contract notice, framework call-off and approval, waiver approval  
**Sample:** 5 items from `off-contract.csv`, where match_class = none, dominant_tag = general_procurement, largest annualised estimate first, 3 payments per supplier, excluding supplier matching /\b(?:COUNCIL|BOROUGH|COUNTY|CNCL|NHS|POLICE|FIRE AUTHORITY|FIRE AND RESCUE|HMRC|HM REVENUE|DEPARTMENT FOR|MINISTRY OF)\b/; 15 transactions

| # | Row ID | Date | Supplier | Amount | Service |
|---|---|---|---|---|---|
| 1 | `Over500_2026_P04_-_published.xlsx:793` | 2026-07-13 | VolkerHighways Ltd | £998,987.64 | Environment |
| 1 | `Over500_2026_P04_-_published.xlsx:603` | 2026-07-28 | VolkerHighways Ltd | £855,750.25 | Environment |
| 1 | `Over500_2026_P03_-_published.xlsx:684` | 2026-06-22 | VolkerHighways Ltd | £366,872.38 | Environment |
| 2 | `Over500_2026_P02_-_published.xlsx:2196` | 2026-05-27 | VEOLIA ES WEST BERKSHIRE LTD (CHAPS ONLY) | £2,201,856.40 | Environment |
| 2 | `Over500_2026_P03_-_published.xlsx:2146` | 2026-06-29 | VEOLIA ES WEST BERKSHIRE LTD (CHAPS ONLY) | £2,180,425.32 | Environment |
| 2 | `Over500_2026_P04_-_published.xlsx:3194` | 2026-07-27 | VEOLIA ES WEST BERKSHIRE LTD (CHAPS ONLY) | £1,803,783.32 | Environment |
| 3 | `Over500_2026_P03_-_published.xlsx:2144` | 2026-06-25 | Millbrook Healthcare Limited | £1,141,918.00 | Finance, Property & Procurement |
| 3 | `Over500_2026_P03_-_published.xlsx:2216` | 2026-06-03 | Millbrook Healthcare Limited | £1,141,918.00 | Finance, Property & Procurement |
| 3 | `Over500_2026_P04_-_published.xlsx:3789` | 2026-07-29 | Millbrook Healthcare Limited | £1,141,918.00 | Finance, Property & Procurement |
| 4 | `Over500_2026_P02_-_published.xlsx:665` | 2026-05-15 | The Better Group Ltd | £64,500.00 | Adult Social Care |
| 4 | `Over500_2026_P02_-_published.xlsx:666` | 2026-05-15 | The Better Group Ltd | £58,833.00 | Adult Social Care |
| 4 | `Over500_2026_P03_-_published.xlsx:670` | 2026-06-01 | The Better Group Ltd | £48,784.37 | Adult Social Care |
| 5 | `Over500_2026_P02_-_published.xlsx:473` | 2026-05-27 | SoftwareONE UK Ltd | £375,697.68 | Transformation, Customer & ICT |
| 5 | `Over500_2026_P02_-_published.xlsx:474` | 2026-05-27 | SoftwareONE UK Ltd | £85,871.04 | Transformation, Customer & ICT |
| 5 | `Over500_2026_P02_-_published.xlsx:653` | 2026-05-27 | SoftwareONE UK Ltd | £59,650.56 | Transformation, Customer & ICT |

**T-04.3. Test.** For each sampled supplier in the lower band, between the three-quote threshold and four times it on an annualised basis, where awards are least likely to predate the notice export, obtain the record behind the spend: the quotation or tender run through the Procurement Portal with its evaluation against notified criteria and its published notice, or the framework call-off with Monitoring Officer approval, or the approved waiver. Confirm the award was made by the officer Appendix A names for its value: the relevant Service Director or a nominated officer below the Threshold, and the Appendix A approval where the value passes the Key Decision threshold. A pass is a record whose route matches the annualised value. A sampled supplier that T-04.1 finds on the contract register is replaced by the next supplier in the same recipe order. Payees matching the analytics' inter-authority pattern are excluded because payments to public bodies are not competed purchases. Trust and fundraising accounts paid as care allowances are also excluded, as they are not purchases of goods or services. [CPR-54, CPR-15, CPR-16, CPR-60, CPR-49, CPR-51, metric:$.tests.off_contract.unmatched_general_procurement.annualised_estimate_gbp]  
**Evidence to inspect:** Portal quotation or tender record, evaluation and award decision, contract notice, framework call-off and approval, waiver approval  
**Sample:** 5 items from `off-contract.csv`, where match_class = none, dominant_tag = general_procurement, annualised estimate ≥ 25000, annualised estimate ≤ 100000, largest annualised estimate first, 3 payments per supplier, excluding supplier matching /\b(?:COUNCIL|BOROUGH|COUNTY|CNCL|NHS|POLICE|FIRE AUTHORITY|FIRE AND RESCUE|HMRC|HM REVENUE|DEPARTMENT FOR|MINISTRY OF)\b|FUNDRAISING/; 13 transactions

| # | Row ID | Date | Supplier | Amount | Service |
|---|---|---|---|---|---|
| 1 | `Over500_2026_P03_-_published.xlsx:1650` | 2026-06-03 | Stripeweb | £2,180.38 | Finance, Property & Procurement |
| 1 | `Over500_2026_P04_-_published.xlsx:641` | 2026-07-02 | Stripeweb | £2,131.94 | Finance, Property & Procurement |
| 1 | `Over500_2026_P02_-_published.xlsx:570` | 2026-05-06 | Stripeweb | £1,988.78 | Finance, Property & Procurement |
| 2 | `Over500_2026_P04_-_published.xlsx:788` | 2026-07-24 | JPAS Contracting Ltd | £18,000.00 | Community Services |
| 2 | `Over500_2026_P02_-_published.xlsx:685` | 2026-05-06 | JPAS Contracting Ltd | £6,235.00 | Community Services |
| 3 | `Over500_2026_P02_-_published.xlsx:200` | 2026-05-26 | ALLSTAR BUSINESS SOLUTIONS LTD | £2,544.81 | Environment |
| 3 | `Over500_2026_P02_-_published.xlsx:199` | 2026-05-26 | ALLSTAR BUSINESS SOLUTIONS LTD | £2,409.29 | Environment |
| 3 | `Over500_2026_P03_-_published.xlsx:148` | 2026-06-15 | ALLSTAR BUSINESS SOLUTIONS LTD | £2,343.27 | Environment |
| 4 | `Over500_2026_P03_-_published.xlsx:692` | 2026-06-15 | SHINFIELD BUILDERS | £10,337.00 | Development & Housing |
| 4 | `Over500_2026_P02_-_published.xlsx:748` | 2026-05-21 | SHINFIELD BUILDERS | £10,010.40 | Development & Housing |
| 5 | `Over500_2026_P04_-_published.xlsx:173` | 2026-07-29 | 1st Transport Innovation Reading Ltd T/A 5 Star Cars & Reading Central Cars | £2,849.50 | Education & SEND |
| 5 | `Over500_2026_P04_-_published.xlsx:343` | 2026-07-27 | 1st Transport Innovation Reading Ltd T/A 5 Star Cars & Reading Central Cars | £2,486.00 | Education & SEND |
| 5 | `Over500_2026_P03_-_published.xlsx:329` | 2026-06-09 | 1st Transport Innovation Reading Ltd T/A 5 Star Cars & Reading Central Cars | £2,224.00 | Education & SEND |


## R-05: Duplicate or repeated payments of the same amount [9 (High; Medium - High)]

**Audit objective.** Conclude whether payments of the same amount to the same supplier within seven days each rest on a distinct purchase, and whether any true duplicate was recovered.

**C-05.1. Expected control.** Written or electronic evidence is held for every purchase, so each payment matches a distinct invoice and order before it is released. [CPR-29] Owner: Accounts Payable.

**T-05.1. Test.** For each sampled general-procurement group paid in the same payment run, match every payment to a distinct invoice and purchase record. Where two payments share an invoice, confirm the duplicate was identified and recovered. [CPR-29, metric:$.tests.duplicates.tiers.same_timestamp.by_tag.general_procurement.groups]  
**Evidence to inspect:** Invoices, purchase orders, payment run reports, credit notes or recovery records  
**Sample:** 10 items from `duplicates.csv`, where tier = same_timestamp, tag = general_procurement, largest gbp_beyond_first first, one item per supplier_norm; 23 transactions

| # | Row ID | Date | Supplier | Amount | Service |
|---|---|---|---|---|---|
| 1 | `Over500_2026_P04_-_published.xlsx:601` | 2026-07-13 | Roadside Technologies Ltd | £9,103.64 | Environment |
| 1 | `Over500_2026_P04_-_published.xlsx:740` | 2026-07-13 | Roadside Technologies Ltd | £9,103.64 | Environment |
| 2 | `Over500_2026_P03_-_published.xlsx:2134` | 2026-06-18 | SEISMIC SEWAGE SYSTEMS LTD | £5,360.00 | Environment |
| 2 | `Over500_2026_P03_-_published.xlsx:2141` | 2026-06-18 | SEISMIC SEWAGE SYSTEMS LTD | £5,360.00 | Environment |
| 3 | `Over500_2026_P04_-_published.xlsx:3663` | 2026-07-29 | MAISHA STAFFING SOLUTIONS LTD | £3,737.50 | Children's Social Care |
| 3 | `Over500_2026_P04_-_published.xlsx:3894` | 2026-07-29 | MAISHA STAFFING SOLUTIONS LTD | £3,737.50 | Children's Social Care |
| 4 | `Over500_2026_P04_-_published.xlsx:162` | 2026-07-21 | COMPASS EXECUTIVE CARS (UK) LTD | £2,178.00 | Education & SEND |
| 4 | `Over500_2026_P04_-_published.xlsx:171` | 2026-07-21 | COMPASS EXECUTIVE CARS (UK) LTD | £2,178.00 | Education & SEND |
| 5 | `Over500_2026_P03_-_published.xlsx:165` | 2026-06-30 | DANIEL GRIFFITHS T/A BLUEBIRD PASSENGER SERVICES | £2,050.00 | Education & SEND |
| 5 | `Over500_2026_P03_-_published.xlsx:334` | 2026-06-30 | DANIEL GRIFFITHS T/A BLUEBIRD PASSENGER SERVICES | £2,050.00 | Education & SEND |
| 6 | `Over500_2026_P03_-_published.xlsx:2413` | 2026-06-25 | AMR CONSULT LTD | £2,046.67 | Education & SEND |
| 6 | `Over500_2026_P03_-_published.xlsx:716` | 2026-06-25 | AMR CONSULT LTD | £2,046.67 | Education & SEND |
| 7 | `Over500_2026_P04_-_published.xlsx:353` | 2026-07-23 | Go Green Taxis Ltd | £962.60 | Children's Social Care |
| 7 | `Over500_2026_P04_-_published.xlsx:357` | 2026-07-23 | Go Green Taxis Ltd | £962.60 | Children's Social Care |
| 7 | `Over500_2026_P04_-_published.xlsx:484` | 2026-07-23 | Go Green Taxis Ltd | £962.60 | Children's Social Care |
| 8 | `Over500_2026_P03_-_published.xlsx:376` | 2026-06-30 | Perceptive On Line Ltd T/A Amatis Networks | £635.64 | Transformation, Customer & ICT |
| 8 | `Over500_2026_P03_-_published.xlsx:392` | 2026-06-30 | Perceptive On Line Ltd T/A Amatis Networks | £635.64 | Transformation, Customer & ICT |
| 8 | `Over500_2026_P03_-_published.xlsx:533` | 2026-06-30 | Perceptive On Line Ltd T/A Amatis Networks | £635.64 | Transformation, Customer & ICT |
| 8 | `Over500_2026_P03_-_published.xlsx:534` | 2026-06-30 | Perceptive On Line Ltd T/A Amatis Networks | £635.64 | Transformation, Customer & ICT |
| 9 | `Over500_2026_P04_-_published.xlsx:160` | 2026-07-14 | FD TRAVELS LIMITED T/A SCHOOL EXPRESS | £1,886.00 | Education & SEND |
| 9 | `Over500_2026_P04_-_published.xlsx:448` | 2026-07-14 | FD TRAVELS LIMITED T/A SCHOOL EXPRESS | £1,886.00 | Education & SEND |
| 10 | `Over500_2026_P03_-_published.xlsx:645` | 2026-06-09 | BPR Ltd trading as We Are Lean and Agile | £1,400.00 | Transformation, Customer & ICT |
| 10 | `Over500_2026_P03_-_published.xlsx:646` | 2026-06-09 | BPR Ltd trading as We Are Lean and Agile | £1,400.00 | Transformation, Customer & ICT |

**T-05.2. Test.** For each sampled general-procurement group paid on different dates within seven days, match every payment to a distinct invoice and purchase record, and confirm whether the repeat reflects a recurring charge under a contract or a second payment of one invoice. [CPR-29, metric:$.tests.duplicates.tiers.different_time.by_tag.general_procurement.groups]  
**Evidence to inspect:** Invoices, purchase orders, contract payment schedule, credit notes or recovery records  
**Sample:** 10 items from `duplicates.csv`, where tier = different_time, tag = general_procurement, largest gbp_beyond_first first, one item per supplier_norm; 27 transactions

| # | Row ID | Date | Supplier | Amount | Service |
|---|---|---|---|---|---|
| 1 | `Over500_2026_P04_-_published.xlsx:3308` | 2026-07-15 | VolkerHighways Ltd | £101,925.86 | Environment |
| 1 | `Over500_2026_P04_-_published.xlsx:618` | 2026-07-17 | VolkerHighways Ltd | £101,925.86 | Environment |
| 2 | `Over500_2026_P02_-_published.xlsx:2160` | 2026-05-12 | TWO SAINTS LTD | £27,147.69 | Development & Housing |
| 2 | `Over500_2026_P02_-_published.xlsx:2161` | 2026-05-13 | TWO SAINTS LTD | £27,147.69 | Development & Housing |
| 3 | `Over500_2026_P04_-_published.xlsx:1288` | 2026-07-13 | Roadside Technologies Ltd | £5,594.11 | Environment |
| 3 | `Over500_2026_P04_-_published.xlsx:598` | 2026-07-13 | Roadside Technologies Ltd | £5,594.11 | Environment |
| 3 | `Over500_2026_P04_-_published.xlsx:734` | 2026-07-13 | Roadside Technologies Ltd | £5,594.11 | Environment |
| 3 | `Over500_2026_P04_-_published.xlsx:789` | 2026-07-13 | Roadside Technologies Ltd | £5,594.11 | Environment |
| 4 | `Over500_2026_P04_-_published.xlsx:259` | 2026-07-13 | BROADWAY CARS | £5,330.00 | Education & SEND |
| 4 | `Over500_2026_P04_-_published.xlsx:264` | 2026-07-13 | BROADWAY CARS | £5,330.00 | Education & SEND |
| 4 | `Over500_2026_P04_-_published.xlsx:474` | 2026-07-13 | BROADWAY CARS | £5,330.00 | Education & SEND |
| 5 | `Over500_2026_P02_-_published.xlsx:8` | 2026-05-13 | Pavillion Publishing and Media Ltd | £9,084.60 | Adult Social Care |
| 5 | `Over500_2026_P02_-_published.xlsx:643` | 2026-05-14 | Pavillion Publishing and Media Ltd | £9,084.60 | Executive Director People - Children's Services |
| 6 | `Over500_2026_P02_-_published.xlsx:187` | 2026-05-11 | CONNICK TREE CARE | £1,009.40 | Environment |
| 6 | `Over500_2026_P02_-_published.xlsx:188` | 2026-05-14 | CONNICK TREE CARE | £1,009.40 | Environment |
| 6 | `Over500_2026_P02_-_published.xlsx:191` | 2026-05-21 | CONNICK TREE CARE | £1,009.40 | Environment |
| 6 | `Over500_2026_P02_-_published.xlsx:197` | 2026-05-28 | CONNICK TREE CARE | £1,009.40 | Environment |
| 6 | `Over500_2026_P03_-_published.xlsx:144` | 2026-06-04 | CONNICK TREE CARE | £1,009.40 | Environment |
| 6 | `Over500_2026_P03_-_published.xlsx:141` | 2026-06-10 | CONNICK TREE CARE | £1,009.40 | Environment |
| 7 | `Over500_2026_P03_-_published.xlsx:459` | 2026-06-25 | LOCAL GOVERNMENT PROPERTY CONSULTANTS (LGPC) | £4,925.00 | Finance, Property & Procurement |
| 7 | `Over500_2026_P03_-_published.xlsx:467` | 2026-06-25 | LOCAL GOVERNMENT PROPERTY CONSULTANTS (LGPC) | £4,925.00 | Finance, Property & Procurement |
| 8 | `Over500_2026_P03_-_published.xlsx:427` | 2026-06-17 | BRITISH TELECOM | £4,364.06 | Transformation, Customer & ICT |
| 8 | `Over500_2026_P03_-_published.xlsx:431` | 2026-06-17 | BRITISH TELECOM | £4,364.06 | Transformation, Customer & ICT |
| 9 | `Over500_2026_P04_-_published.xlsx:467` | 2026-07-09 | FD TRAVELS LIMITED T/A SCHOOL EXPRESS | £4,018.00 | Education & SEND |
| 9 | `Over500_2026_P04_-_published.xlsx:266` | 2026-07-14 | FD TRAVELS LIMITED T/A SCHOOL EXPRESS | £4,018.00 | Education & SEND |
| 10 | `Over500_2026_P04_-_published.xlsx:635` | 2026-07-14 | AMR CONSULT LTD | £2,665.27 | Education & SEND |
| 10 | `Over500_2026_P04_-_published.xlsx:838` | 2026-07-14 | AMR CONSULT LTD | £2,665.27 | Education & SEND |

**T-05.3. Test.** For the largest placement groups, confirm the repeated payments relate to different service users or different periods by matching each to its care package or placement invoice. [CPR-29, metric:$.tests.duplicates.tiers.same_timestamp.by_tag.care_or_education_placement.groups]  
**Evidence to inspect:** Placement invoices, care package records showing the service user and period  
**Sample:** 10 items from `duplicates.csv`, where tag = care_or_education_placement, largest gbp_beyond_first first, largest 2 payments per item, one item per supplier_norm; 20 transactions

| # | Row ID | Date | Supplier | Amount | Service |
|---|---|---|---|---|---|
| 1 | `Over500_2026_P03_-_published.xlsx:2164` | 2026-06-17 | Oaklands SEN School Berkshire Limited | £20,337.45 | Education (DSG Funded) & Other Education Grants |
| 1 | `Over500_2026_P03_-_published.xlsx:2165` | 2026-06-17 | Oaklands SEN School Berkshire Limited | £20,337.45 | Education (DSG Funded) & Other Education Grants |
| 2 | `Over500_2026_P02_-_published.xlsx:2242` | 2026-05-19 | Phoenix Child Care Limited -The Grange School | £21,988.16 | Education (DSG Funded) & Other Education Grants |
| 2 | `Over500_2026_P02_-_published.xlsx:2243` | 2026-05-19 | Phoenix Child Care Limited -The Grange School | £21,988.16 | Education (DSG Funded) & Other Education Grants |
| 3 | `Over500_2026_P04_-_published.xlsx:1040` | 2026-07-08 | BUPA Care Services | £8,476.52 | Adult Social Care |
| 3 | `Over500_2026_P04_-_published.xlsx:1041` | 2026-07-08 | BUPA Care Services | £8,476.52 | Adult Social Care |
| 4 | `Over500_2026_P03_-_published.xlsx:2157` | 2026-06-03 | Sukhbir Singh and Harvinder Singh T/A Calcot Services for Children (CSFC) | £18,768.75 | Education (DSG Funded) & Other Education Grants |
| 4 | `Over500_2026_P03_-_published.xlsx:2158` | 2026-06-03 | Sukhbir Singh and Harvinder Singh T/A Calcot Services for Children (CSFC) | £18,768.75 | Education (DSG Funded) & Other Education Grants |
| 5 | `Over500_2026_P02_-_published.xlsx:2266` | 2026-05-26 | Huckleberry House | £30,918.75 | Education (DSG Funded) & Other Education Grants |
| 5 | `Over500_2026_P02_-_published.xlsx:2267` | 2026-05-26 | Huckleberry House | £30,918.75 | Education (DSG Funded) & Other Education Grants |
| 6 | `Over500_2026_P03_-_published.xlsx:1015` | 2026-06-17 | GCH (Alder) Ltd t/a Hungerford Care Home | £5,700.00 | Adult Social Care |
| 6 | `Over500_2026_P03_-_published.xlsx:1383` | 2026-06-17 | GCH (Alder) Ltd t/a Hungerford Care Home | £5,700.00 | Adult Social Care |
| 7 | `Over500_2026_P04_-_published.xlsx:3064` | 2026-07-16 | Paradigm Care Services Ltd. | £17,000.00 | Children's Social Care |
| 7 | `Over500_2026_P04_-_published.xlsx:3091` | 2026-07-22 | Paradigm Care Services Ltd. | £17,000.00 | Children's Social Care |
| 8 | `Over500_2026_P03_-_published.xlsx:1931` | 2026-06-16 | Care Services To You | £23,989.77 | Children's Social Care |
| 8 | `Over500_2026_P03_-_published.xlsx:2008` | 2026-06-16 | Care Services To You | £23,989.77 | Children's Social Care |
| 9 | `Over500_2026_P02_-_published.xlsx:2092` | 2026-05-26 | Amegreen Childrens Services | £34,431.08 | Children's Social Care |
| 9 | `Over500_2026_P02_-_published.xlsx:2105` | 2026-05-27 | Amegreen Childrens Services | £34,431.08 | Children's Social Care |
| 10 | `Over500_2026_P03_-_published.xlsx:1716` | 2026-06-24 | Affinity Trust Support Ltd | £3,960.00 | Adult Social Care |
| 10 | `Over500_2026_P03_-_published.xlsx:2958` | 2026-06-24 | Affinity Trust Support Ltd | £3,960.00 | Adult Social Care |


## R-06: Spend continuing after the published contract has ended [6 (Moderate; Moderate)]

**Audit objective.** Conclude whether payments to suppliers whose published notices had all ended before the spend window are covered by a current contract or an approved extension.

**C-06.1. Expected control.** A contract that provides for extension is extended only with S151 Officer approval, recorded before the original term ends, and the extension is entered on the contract register. [CPR-61, CPR-05] Owner: S151 Officer.

**T-06.1. Test.** For each sampled supplier, obtain the contract under which the sampled payments were made. Where it is the expired contract, obtain the S151 Officer's extension approval and confirm it predates the original end date. Where it is a newer contract, confirm it is on the register and record why no notice was published. A pass is a contract or approved extension covering the payment date. Every flagged supplier is tested; the register calls this a small, fully testable population. [CPR-61, CPR-28, metric:$.tests.expired_notice_spend.suppliers]  
**Evidence to inspect:** Contract, S151 extension approval, contract register entry, procurement file  
**Sample:** 7 items from `expired-notice-spend.csv`, largest total_gbp first, 3 payments per supplier, (only 7 available); 11 transactions

| # | Row ID | Date | Supplier | Amount | Service |
|---|---|---|---|---|---|
| 1 | `Over500_2026_P03_-_published.xlsx:704` | 2026-06-16 | Hope & Clay (Construction) Ltd | £91,306.75 | Environment |
| 2 | `Over500_2026_P03_-_published.xlsx:58` | 2026-06-03 | BERKSHIRE MECHANICAL SERVICES | £8,250.00 | Development & Housing |
| 2 | `Over500_2026_P03_-_published.xlsx:42` | 2026-06-03 | BERKSHIRE MECHANICAL SERVICES | £6,250.00 | Development & Housing |
| 2 | `Over500_2026_P03_-_published.xlsx:279` | 2026-06-09 | BERKSHIRE MECHANICAL SERVICES | £5,585.00 | Development & Housing |
| 3 | `Over500_2026_P02_-_published.xlsx:467` | 2026-05-08 | G7 BUSINESS SOLUTIONS LIMITED | £5,469.78 | Finance, Property & Procurement |
| 3 | `Over500_2026_P03_-_published.xlsx:531` | 2026-06-10 | G7 BUSINESS SOLUTIONS LIMITED | £5,469.78 | Finance, Property & Procurement |
| 3 | `Over500_2026_P03_-_published.xlsx:721` | 2026-06-10 | G7 BUSINESS SOLUTIONS LIMITED | £1,365.00 | Finance, Property & Procurement |
| 4 | `Over500_2026_P02_-_published.xlsx:459` | 2026-05-15 | CACI Limited | £12,071.67 | Children's Social Care |
| 5 | `Over500_2026_P03_-_published.xlsx:686` | 2026-06-22 | Morton Pattison Ltd | £1,102.00 | Environment |
| 6 | `Over500_2026_P03_-_published.xlsx:821` | 2026-06-03 | Davis and Associates Consultancy Limited | £800.00 | Chief Executive |
| 7 | `Over500_2026_P04_-_published.xlsx:58` | 2026-07-20 | Tactical Facilities Management Ltd | £681.94 | Development & Housing |


## R-07: Spend running above the awarded contract value without an approved variation [12 (High; Medium - High)]

**Audit objective.** Conclude whether spend running above a contract's awarded annual rate is covered by the contract value or by an approved variation.

**C-07.1. Expected control.** Variations of scope or value are approved before they take effect: by the Monitoring Officer and S151 Officer below the Threshold, and by the relevant board on their recommendation above it. [CPR-62, CPR-63] Owner: Monitoring Officer and S151 Officer.

**T-07.1. Test.** For each sampled supplier, obtain the signed contract and compare its value and term with spend to date. Confirm whether the published award value was an estimate or a maximum. Where spend exceeds the contract value, obtain the variation approval and confirm it predates the extra spend. A pass is spend within the contract value or an approved variation covering it. Every flagged supplier is tested. [CPR-62, CPR-63, metric:$.tests.spend_vs_award.flagged]  
**Evidence to inspect:** Signed contract, contract spend report, variation approval, board report where the value requires one  
**Sample:** 12 items from `spend-vs-award.csv`, where ratio ≥ 1.25, largest total_gbp first, 3 payments per supplier; 28 transactions

| # | Row ID | Date | Supplier | Amount | Service |
|---|---|---|---|---|---|
| 1 | `Over500_2026_P02_-_published.xlsx:437` | 2026-05-20 | Newbury & District Ltd | £60,797.19 | Environment |
| 1 | `Over500_2026_P03_-_published.xlsx:267` | 2026-06-01 | Newbury & District Ltd | £59,626.76 | Environment |
| 1 | `Over500_2026_P03_-_published.xlsx:270` | 2026-06-30 | Newbury & District Ltd | £59,007.20 | Environment |
| 2 | `Over500_2026_P04_-_published.xlsx:905` | 2026-07-22 | NEC SOFTWARE SOLUTIONS UK LIMITED | £129,125.00 | Finance, Property & Procurement |
| 2 | `Over500_2026_P04_-_published.xlsx:492` | 2026-07-22 | NEC SOFTWARE SOLUTIONS UK LIMITED | £91,629.15 | Finance, Property & Procurement |
| 2 | `Over500_2026_P04_-_published.xlsx:487` | 2026-07-22 | NEC SOFTWARE SOLUTIONS UK LIMITED | £52,054.00 | Finance, Property & Procurement |
| 3 | `Over500_2026_P03_-_published.xlsx:2130` | 2026-06-09 | TWO SAINTS LTD | £38,775.00 | Development & Housing |
| 3 | `Over500_2026_P04_-_published.xlsx:3181` | 2026-07-22 | TWO SAINTS LTD | £38,775.00 | Development & Housing |
| 3 | `Over500_2026_P02_-_published.xlsx:2160` | 2026-05-12 | TWO SAINTS LTD | £27,147.69 | Development & Housing |
| 4 | `Over500_2026_P04_-_published.xlsx:321` | 2026-07-14 | FD TRAVELS LIMITED T/A SCHOOL EXPRESS | £4,074.00 | Education & SEND |
| 4 | `Over500_2026_P04_-_published.xlsx:266` | 2026-07-14 | FD TRAVELS LIMITED T/A SCHOOL EXPRESS | £4,018.00 | Education & SEND |
| 4 | `Over500_2026_P04_-_published.xlsx:467` | 2026-07-09 | FD TRAVELS LIMITED T/A SCHOOL EXPRESS | £4,018.00 | Education & SEND |
| 5 | `Over500_2026_P04_-_published.xlsx:1276` | 2026-07-22 | WCL UK Ltd (Trading as Everything ICT) | £102,882.78 | Education & SEND |
| 6 | `Over500_2026_P03_-_published.xlsx:371` | 2026-06-08 | IDOX SOFTWARE LTD | £48,579.20 | Community Services |
| 6 | `Over500_2026_P02_-_published.xlsx:462` | 2026-05-20 | IDOX SOFTWARE LTD | £2,647.21 | Development & Housing |
| 7 | `Over500_2026_P04_-_published.xlsx:207` | 2026-07-22 | ACE WHEELCHAIR TRAVEL | £4,840.00 | Education & SEND |
| 7 | `Over500_2026_P04_-_published.xlsx:328` | 2026-07-29 | ACE WHEELCHAIR TRAVEL | £3,916.00 | Education & SEND |
| 7 | `Over500_2026_P04_-_published.xlsx:445` | 2026-07-22 | ACE WHEELCHAIR TRAVEL | £3,520.00 | Education & SEND |
| 8 | `Over500_2026_P03_-_published.xlsx:396` | 2026-06-10 | BookingLab Limited | £24,000.00 | Transformation, Customer & ICT |
| 9 | `Over500_2026_P04_-_published.xlsx:313` | 2026-07-08 | Valley Cars | £3,173.00 | Education & SEND |
| 9 | `Over500_2026_P03_-_published.xlsx:222` | 2026-06-02 | Valley Cars | £2,505.00 | Education & SEND |
| 9 | `Over500_2026_P02_-_published.xlsx:354` | 2026-05-06 | Valley Cars | £2,338.00 | Education & SEND |
| 10 | `Over500_2026_P03_-_published.xlsx:384` | 2026-06-04 | Exacom Systems Ltd | £12,105.85 | Development & Housing |
| 11 | `Over500_2026_P02_-_published.xlsx:460` | 2026-05-20 | Softcat Ltd | £8,979.02 | Education & SEND |
| 11 | `Over500_2026_P03_-_published.xlsx:375` | 2026-06-17 | Softcat Ltd | £2,025.98 | Transformation, Customer & ICT |
| 12 | `Over500_2026_P03_-_published.xlsx:276` | 2026-06-30 | SMS-Environmental Ltd | £2,070.00 | Adult Social Care |
| 12 | `Over500_2026_P04_-_published.xlsx:365` | 2026-07-09 | SMS-Environmental Ltd | £1,335.60 | Adult Social Care |
| 12 | `Over500_2026_P03_-_published.xlsx:29` | 2026-06-22 | SMS-Environmental Ltd | £1,175.00 | Adult Social Care |


## R-08: Waivers and exceptions granted without the required approval [6 (Moderate; Moderate)]

**Audit objective.** Conclude whether waivers and exceptions in the audit period were documented, justified and approved in advance by the officer and board the Rules name for their value.

**C-08.1. Expected control.** Every waiver or exception is fully documented, reported in writing to the relevant board in advance where competition is not excluded, and approved by the S151 Officer, who records that the reasons were considered. [CPR-18, CPR-22, CPR-23, CPR-24] Owner: S151 Officer.

**T-08.1. Test.** Obtain the waiver and exception log for the spend window. For each entry, confirm a documented reason, an advance written report to the board where competition was not excluded, and the S151 Officer's recorded approval. Ask which approver the council treats as authoritative, given that one clause names the relevant Executive Director or Chief Executive and another names only the Monitoring Officer or S151 Officer. [CPR-17, CPR-18, CPR-22, CPR-24]  
**Evidence to inspect:** Waiver and exception log, waiver forms, board reports, S151 approval records  
**Sample:** document test over the full waiver and exception log for the spend window; the log is not in the published data

**C-08.2. Expected control.** Approval follows the value bands: the S151 Officer up to the Threshold, the S151 Officer after consulting the Monitoring Officer and Executive Director with a board-approved report up to the Key Decision threshold, and the Executive above it; exclusions, framework awards without competition and exemptions above the Threshold carry prior Monitoring Officer or board approval. [CPR-19, CPR-20, CPR-21, CPR-58, CPR-60, CPR-65] Owner: S151 Officer and Monitoring Officer.

**T-08.2. Test.** For each log entry, compare the contract value with the approver recorded and confirm it matches the value band in the Rules. For exclusions, framework awards without further competition and exemptions above the Threshold, confirm the prior Monitoring Officer or board approval is on file. [CPR-19, CPR-20, CPR-21, CPR-58, CPR-65]  
**Evidence to inspect:** Waiver and exception log, exception reports, board and Executive minutes, Monitoring Officer approvals  
**Sample:** document test over the same log entries as T-08.1


## R-09: Care and education placements without the recorded reasons for provider choice [12 (High; Medium - High)]

**Audit objective.** Conclude whether care and education placements, which are exempt from competition, carry the record of reasons for the choice of provider and, where it applies, the Provider Selection Regime process.

**C-09.1. Expected control.** The reasons for the choice of provider are recorded on the individual's case notes, and key decisions under the Provider Selection Regime are recorded with its process followed. [CPR-64, CPR-59] Owner: Relevant Service Director.

**T-09.1. Test.** For each sampled placement payment, identify the service user and placement it pays for and inspect the case notes for the recorded reasons for the provider chosen. Where the Provider Selection Regime applies, confirm the key decisions are recorded and its process was followed. A pass is a dated reason on the case notes for the placement paid. [CPR-64, CPR-59, metric:$.population.tags.care_or_education_placement.gbp]  
**Evidence to inspect:** Case notes, placement agreement, Provider Selection Regime decision record  
**Sample:** 10 items from `spend-clean.csv`, where tag = care_or_education_placement, largest Net amount first, one item per supplier_norm, excluding suppliers and rows already drawn in T-05.3; 10 transactions

| # | Row ID | Date | Supplier | Amount | Service |
|---|---|---|---|---|---|
| 1 | `Over500_2026_P04_-_published.xlsx:3242` | 2026-07-29 | Engaging Potential Ltd | £272,549.17 | Education (DSG Funded) & Other Education Grants |
| 2 | `Over500_2026_P02_-_published.xlsx:823` | 2026-05-13 | RUSKIN MILL TRUST | £179,236.76 | Adult Social Care |
| 3 | `Over500_2026_P04_-_published.xlsx:3077` | 2026-07-06 | Early Rise Care Ltd. | £126,091.62 | Children's Social Care |
| 4 | `Over500_2026_P04_-_published.xlsx:2729` | 2026-07-22 | PBT SOCIAL CARE LTD | £94,446.00 | Adult Social Care |
| 5 | `Over500_2026_P02_-_published.xlsx:2124` | 2026-05-27 | Camino Care | £94,040.67 | Children's Social Care |
| 6 | `Over500_2026_P02_-_published.xlsx:2031` | 2026-05-12 | Changing Lives Care Group Ltd | £89,014.28 | Children's Social Care |
| 7 | `Over500_2026_P04_-_published.xlsx:3476` | 2026-07-29 | Brighter Living Care Ltd | £78,599.04 | Adult Social Care |
| 8 | `Over500_2026_P04_-_published.xlsx:3767` | 2026-07-02 | Heart and Home Living Ltd. | £66,340.00 | Children's Social Care |
| 9 | `Over500_2026_P02_-_published.xlsx:2030` | 2026-05-11 | Spring Valley Children's Care Homes ltd | £58,457.14 | Children's Social Care |
| 10 | `Over500_2026_P02_-_published.xlsx:2022` | 2026-05-05 | North Star Children's Homes Ltd. | £58,257.61 | Children's Social Care |

**T-09.2. Test.** For each sampled direct payment, confirm the case notes record the reasons for the personalised package and the provider or arrangement chosen, and that the payment matches the agreed personal budget. This stratum tests the theme of the Limited opinion on Personal Budgets (Direct Payments). The spend data identifies direct payments only by the Adult Social Care narrative 'Direct Payment'; direct payments for children cannot be identified in it. [CPR-64, metric:$.population.tags.care_or_education_placement.gbp]  
**Evidence to inspect:** Case notes, personal budget agreement, direct payment agreement and monitoring record  
**Sample:** 2 items from `spend-clean.csv`, where Narrative = Direct Payment, largest Net amount first, one item per supplier_norm, (only 2 available); 2 transactions

| # | Row ID | Date | Supplier | Amount | Service |
|---|---|---|---|---|---|
| 1 | `Over500_2026_P02_-_published.xlsx:2757` | 2026-05-22 | Solo Support Services | £6,577.72 | Adult Social Care |
| 2 | `Over500_2026_P02_-_published.xlsx:2688` | 2026-05-20 | CareMatch Ltd | £4,149.72 | Adult Social Care |


## Prepared-by-client (PBC) request list

Derived from the test steps above. Each item names the tests that need it.

| # | Risk | Item requested | For tests |
|---|---|---|---|
| 1 | R-01 | Purchase orders and requirement value estimates for the sampled payments | T-01.1 |
| 2 | R-01 | Procurement Portal quotation records, quotes received and evaluation for the sampled payments | T-01.1 |
| 3 | R-02 | Purchase orders and invoices for every payment in the sampled windows | T-02.1, T-02.2 |
| 4 | R-02 | Quotation, tender, contract or framework call-off record covering each sampled supplier | T-02.1, T-02.2 |
| 5 | R-03 | Award report, Key Decision record and Appendix A approvals for the contracts behind the sampled windows | T-03.1 |
| 6 | R-03 | Award approvals (report, Key Decision record, board or Executive approval) for the contracts held by the sampled suppliers | T-03.2 |
| 7 | R-04 | Contract register as at the end of the spend window, with value, duration and supplier | T-04.1 |
| 8 | R-04 | Quotation, tender, framework call-off or waiver record for each sampled supplier | T-04.2, T-04.3 |
| 9 | R-04 | Contract notice and award decision for each sampled supplier | T-04.2, T-04.3 |
| 10 | R-05 | Invoices and purchase orders for every payment in the sampled duplicate groups | T-05.1, T-05.2 |
| 11 | R-05 | Credit notes or recovery records for any duplicate identified | T-05.1 |
| 12 | R-05 | Contract payment schedules for the sampled suppliers | T-05.2 |
| 13 | R-05 | Placement invoices and care package references for the sampled placement groups | T-05.3 |
| 14 | R-06 | Current contract or S151 extension approval for each sampled supplier | T-06.1 |
| 15 | R-07 | Signed contracts and contract spend to date for the sampled suppliers | T-07.1 |
| 16 | R-07 | Variation approvals for the sampled suppliers | T-07.1 |
| 17 | R-08 | Waiver and exception log for the spend window, with the approval record for each entry | T-08.1 |
| 18 | R-08 | Exception reports and the board, Executive or Monitoring Officer approvals for each log entry | T-08.2 |
| 19 | R-09 | Case notes recording the reasons for provider choice for the sampled placements | T-09.1 |
| 20 | R-09 | Provider Selection Regime decision records where the regime applies | T-09.1 |
| 21 | R-09 | Case notes and direct payment agreements for the sampled direct payments | T-09.2 |
