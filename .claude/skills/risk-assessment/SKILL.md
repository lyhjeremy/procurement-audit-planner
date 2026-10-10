---
name: risk-assessment
description: Method for turning rules.json, analytics.json and history.json into a rated procurement risk register. The agent writes cited judgments to outputs/risk-ratings.json; build_register.py resolves every citation, fills every figure, scores on the council's own matrix, renders outputs/risk-register.md and writes the outputs/auditor-comments.md decision template. Loaded by the risk-assessor sub-agent.
---

# risk-assessment

Turn three verified inputs into a risk register a human auditor can approve,
amend or reject. The model judges likelihood and impact; the builder computes
the score, the matrix label, the band and every figure. A rating that cannot
be traced to a rule, a metric or an audit item does not reach the register.

## Inputs and outputs

| | Path |
| --- | --- |
| Rules | `outputs/rules.json` (cite as `[rule:CPR-nn]`) |
| Analytics | `outputs/analytics.json` (cite as `[metric:$.json.path]`) |
| History | `outputs/history.json` (cite as `[history:ID]`, e.g. `AUD-16`, `RT-03`, `D-04`, or `[history:$.json.path]`) |
| Your judgments | `outputs/risk-ratings.json` (you write this) |
| Builder | `.claude/skills/risk-assessment/build_register.py` |
| Register | `outputs/risk-register.md` (builder writes) |
| Decision template | `outputs/auditor-comments.md` (builder writes; the auditor fills it in) |

Run the builder with `.venv/bin/python .claude/skills/risk-assessment/build_register.py`.
It exits 0 when there are no failures. Stop and report if any input is missing.

## Rules that do not bend

1. **Every likelihood and every impact justification cites at least one
   resolvable source**: `[rule:ID]`, `[metric:$.path]` or `[history:ID]`. A
   risk whose likelihood or impact justification has none is dropped by the
   builder and listed as "excluded by validation".
2. **No typed figures.** Every number from the data is a `{{$.path}}`
   placeholder that the builder fills from analytics.json. A `£` amount or a
   number of three or more digits typed in prose is a warning; treat
   warnings as failures. Scores (1–5) are the only digits you write.
3. **Indicator language.** Risks describe patterns to investigate: "may
   indicate", "indicator of", "consistent with". Never "fraud", "breach" as
   fact, or "non-compliant" about a named body. No supplier, officer or
   department appears in a statement, a justification or a focus line.
   Supplier names may appear only in evidence labels quoting a top-20 row.
4. **Repeat findings.** If an audit on the same theme carries an adverse
   opinion (Limited, Weak, Unsatisfactory, No assurance), raise likelihood by
   one point (max 5), say so in `repeat_uplift`, and cite that audit. The
   builder fails an uplift that cites an audit without an adverse opinion,
   and fails one whose likelihood is not `base_score` + 1. A strict repeat is
   a follow-up that found actions still not implemented, or adverse opinions
   on the theme more than once; an uplift resting on one first-time adverse
   opinion builds with a warning, so say plainly in the justification that it
   is a first adverse opinion and leave the auditor to confirm it at the gate.
5. **Never resolve a conflict in the scoring method silently.** The builder
   uses Table 4 bands and marks the Figure 4 rule in its own column and in the
   header; you do the same in prose.
6. **You recommend scope; the auditor decides.** `recommend_in_scope` is a
   recommendation with a one-line `scope_reason`.

## Step 1: Read the inputs

Read `rules.json` (types, thresholds, parameters, notes), the full
`analytics.json` (each test's parameters, counts, totals, caveats) and
`history.json` (audits and opinions, risk themes, `scoring_method`, gaps,
discrepancies). Note which metric paths are scalars: only scalars can be
cited or used as placeholders (`$.tests.split_purchases.per_threshold[0].windows` yes,
`$.tests.split_purchases.per_threshold` no; `$.tests.split_purchases.per_threshold[0].gbp`
yes).

## Step 2: Work theme by theme

Consider every theme below. Rate it, or exclude it in `excluded` with a
one-line reason. Do not invent themes the inputs do not support.

| Theme | Rules to look for | Metrics to look for | History to look for |
| --- | --- | --- | --- |
| Quotes and tenders not obtained near thresholds | threshold rows of App B, quote/tender rules | `threshold_clustering` | Contract Letting audit, procurement risk themes |
| Contracts split to stay under a threshold | anti-avoidance rule | `split_purchases` | fraud and financial-control themes |
| Spend above the tender threshold with no published contract | tender, publication and contract-register rules | `off_contract`, `high_value_suppliers` | Contract Letting audit |
| Duplicate or repeated payments | payment/approval rules | `duplicates` | Accounts Payable audit |
| Spend continuing after a contract has expired | extension rules (App C row D) | `expired_notice_spend` | contract management themes |
| Spend beyond the awarded value without a variation | variation rules (App C row E) | `spend_vs_award` | contract management themes |
| Waivers and exemptions from competition | waiver clauses | none observable | discrepancies in the waiver clauses |
| Approvals and delegated authority (Key Decisions, award sign-off) | approver rules, App A | high-value awards if any metric exists | governance themes |
| Care placements and direct payments procured outside the Rules | exemptions for care, if any | spend by service if present | Direct Payments and residential care audits |

Where a mandatory control has no observable metric (waivers, approvals,
register completeness), rate it on the rule and the gap, and say in the
justification that the data cannot see it.

## Step 3: Score on the council's scale

Use `history.json → scoring_method`: likelihood 1 Rare … 5 Certain, impact
1 Negligible … 5 Critical. If `scoring_method.usable` is false, use 1–5 Very
low … Very high; the builder states the fallback in the header.

**Likelihood rubric** (so two runs rate the same evidence the same way):

| Score | Use when |
| --- | --- |
| 1 Rare | No metric flags the pattern and no adverse audit on the theme; the rule is clear. |
| 2 Unlikely | A weak signal (few flags, or flags in a single month), or a control the data cannot see with no adverse history. |
| 3 Likely | A clear signal: flags across more than one month or more than a handful of suppliers; or an adverse audit on the theme with no data signal. |
| 4 Almost Certain | A strong signal: many flags across all months in the window, or a flagged total that is material against the threshold it relates to. |
| 5 Certain | Two independent metrics show the same pattern, widespread across the window. |

Then apply rule 4 (repeat uplift) on top, at most once per risk.

**Impact method.** Compare the £ exposure the risk rests on (cite the metric;
prefer an annualised estimate where the analytics give one) with the
`impact_scale` financial bands, then adjust by at most one point for the
compliance or reputation descriptors of the same scale (statutory
procurement rules, publication duties). State which band you used. You
compare values against bands; you never compute a new figure.

## Step 4: Write `outputs/risk-ratings.json`

```json
{
  "generated_at": "YYYY-MM-DD",
  "risks": [
    {
      "id": "R-01",
      "title": "Short qualitative risk title, no figures",
      "statement": "Payments clustering just under a quote threshold may indicate quotes not being sought [rule:CPR-53].",
      "likelihood": {"score": 3, "justification": "{{$.tests.threshold_clustering.per_threshold[1].band_count}} payments sit just below the threshold [metric:$.tests.threshold_clustering.per_threshold[1].band_count], against {{$.tests.threshold_clustering.per_threshold[1].comparator_count}} just above it [metric:$.tests.threshold_clustering.per_threshold[1].comparator_count]."},
      "impact": {"score": 3, "justification": "The flagged total of £{{$.tests.threshold_clustering.per_threshold[1].band_gbp}} falls in the Medium band [metric:$.tests.threshold_clustering.per_threshold[1].band_gbp]; quotation duties are mandatory [rule:CPR-53]."},
      "repeat_uplift": null,
      "evidence": ["rule:CPR-53", "metric:$.tests.threshold_clustering.per_threshold[1].band_count", "history:AUD-01"],
      "proposed_focus": "What fieldwork should test, in one or two sentences.",
      "recommend_in_scope": true,
      "scope_reason": "One line.",
      "sample_source": "threshold-clustering.csv"
    }
  ],
  "excluded": [
    {"theme": "Theme name", "reason": "One line: why it is not rated."}
  ]
}
```

- `id`: `R-01`, `R-02`, … in order. Keep IDs stable on a revision.
- `repeat_uplift`, when applied: `{"cites": "history:AUD-16", "base_score": 2, "justification": "... [history:AUD-16]"}`.
  The likelihood `score` you write already includes the +1; `base_score` is
  the score before it. `cites` may be a list when several audits apply.
- `evidence`: citation strings without brackets. The builder renders rule
  evidence as a quote excerpt from rules.json, metrics with their value, and
  history items with their opinion and page.
- `sample_source`: the file in `outputs/analytics-full/` fieldwork would
  sample from, or `""` when the risk has no transaction population.

**Revision (re-run after the gate only).** When the auditor has recorded
decisions in `outputs/auditor-comments.md`, add:

```json
"revision": {"number": 1, "changed": [{"id": "R-09", "as": "amended"}, {"id": "R-10", "as": "rejected"}]}
```

Approved risks stay exactly as they were. Amendments are applied exactly as
asked; if the auditor's score is not one the evidence alone supports, keep it,
set `"auditor_override": true` and quote the comment inside the justification
next to at least one real citation. Rejected risks leave `risks` and go to
`excluded` as `{"id": "R-10", "theme": "...", "reason": "Auditor: <comment>"}`.

## Step 5: Build and fix

Run the builder. It:

1. resolves every citation and fills every placeholder (FAIL when one does
   not resolve; a risk whose likelihood or impact has no resolvable citation
   is dropped and counted);
2. computes `score = likelihood × impact`, the matrix label from
   `scoring_method.combination.matrix`, and the band from
   `scoring_method.bands` (Table 4); it marks the Figure 4 escalation rule
   next to it and names the conflict in the header;
3. checks every repeat uplift cites an audit with an adverse opinion and
   adds exactly one point to `base_score`, and warns when the uplift rests on
   one first-time adverse opinion rather than a repeat;
4. warns on typed figures;
5. renders `outputs/risk-register.md` (header, summary table, one section per
   risk, excluded themes, and a closing "Auditor decisions" section);
6. writes `outputs/auditor-comments.md`, one row per rated risk with blank
   Decision and Comment cells, keeping every decision already recorded;
7. on a revision, checks that every recorded decision was applied, that
   nothing else changed since the previous version, and writes the revision
   header from your `revision` block. "Nothing else changed" covers title,
   statement, scores, scope, justifications, evidence, focus, scope reason,
   uplift, override and sample source; a risk listed as amended must differ
   from the previous version.

Fix every FAIL and every WARN by correcting the ratings file, never by editing
the builder or the register. Re-run until `warnings: 0, failures: 0`. The one
exception is the first-time adverse opinion warning on an uplift you keep:
report it, so the auditor confirms or removes the uplift at the gate.

## Step 6: Report

Under 400 words: the method used (and any fallback or conflict), a table of
risks (ID, title, L × I = score, band, recommended scope), what was excluded
and why, anything the data cannot see, and, on a first run, an explicit
request that the auditor record a decision (approve, amend or reject) for
each risk in `outputs/auditor-comments.md`.
