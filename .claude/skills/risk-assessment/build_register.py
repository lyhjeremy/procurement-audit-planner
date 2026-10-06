#!/usr/bin/env python3
"""Validate outputs/risk-ratings.json and render the risk register.

Usage: build_register.py [RATINGS_JSON]
       [--rules outputs/rules.json] [--analytics outputs/analytics.json]
       [--history outputs/history.json] [--comments outputs/auditor-comments.md]
       [--out-dir outputs]

Checks
  citations   [rule:ID], [metric:$.path] (scalar) and [history:ID|$.path]
              resolve; a risk whose likelihood or impact justification has no
              resolvable citation is dropped ("excluded by validation").
  figures     {{$.path}} placeholders are filled from analytics.json; a figure
              typed in prose is a warning.
  scores      likelihood and impact are integers 1-5; the builder computes the
              score, the matrix label (scoring_method.combination.matrix) and
              the band (scoring_method.bands, i.e. Table 4).
  uplift      a repeat-finding uplift cites an audit with an adverse opinion.
  revision    when auditor-comments.md holds decisions: the ratings file has a
              revision block, every decision is applied, and nothing changed
              that the auditor did not ask for (compared with the previous
              version's snapshot in outputs/.register-versions/).
Writes outputs/risk-register.md and outputs/auditor-comments.md (decisions
already recorded are kept). Exit 0 when no failures; exit 1 otherwise.
"""
import argparse, datetime, json, re, sys
from collections import OrderedDict
from pathlib import Path

CITE_RE = re.compile(r"\[(rule|metric|history):((?:[^\[\]]|\[\d+\])+)\]")
PH_RE = re.compile(r"\{\{(\$[^}]+)\}\}")
NUM_RE = re.compile(r"£\s?\d|\b\d{3,}\b")
ADVERSE = re.compile(r"\b(limited|weak|unsatisfactory|no assurance|minimal)\b", re.I)
DECISIONS = {"approve", "amend", "reject"}
FALLBACK_L = {1: "Very low", 2: "Low", 3: "Medium", 4: "High", 5: "Very high"}


def jpath(obj, path):
    """Resolve $.a.b[0].c against obj; return (found, value)."""
    if not path.startswith("$"):
        return False, None
    cur = obj
    for key, idx in re.findall(r"\.([^.\[\]]+)|\[(\d+)\]", path[1:]):
        try:
            cur = cur[int(idx)] if idx else cur[key]
        except (KeyError, IndexError, TypeError):
            return False, None
    return True, cur


def fmt(v):
    if isinstance(v, bool) or v is None:
        return str(v)
    if isinstance(v, float):
        return f"{v:,.2f}" if v != int(v) else f"{int(v):,}"
    if isinstance(v, int):
        return f"{v:,}"
    return str(v)


def cell(s):
    return str(s).replace("|", "/").replace("\n", " ").strip()


def history_index(h):
    """ID -> item for every citable history item."""
    idx = {}
    for key in ("audits", "risk_themes", "discrepancies"):
        for it in h.get(key) or []:
            if isinstance(it, dict) and it.get("id"):
                idx[it["id"]] = it
    for it in (h.get("scoring_method") or {}).get("discrepancies") or []:
        if isinstance(it, dict) and it.get("id"):
            idx.setdefault(it["id"], it)
    for it in h.get("gaps") or []:
        if isinstance(it, dict) and it.get("item"):
            idx.setdefault(it["item"], it)
    return idx


def read_comments(path):
    out = {"reviewer": "", "date": "", "rows": OrderedDict()}
    if not path.exists():
        return out
    text = path.read_text(encoding="utf-8")
    m = re.search(r"^Reviewer:[ \t]*(.*)$", text, re.M)
    out["reviewer"] = m.group(1).strip() if m else ""
    m = re.search(r"^Date:[ \t]*(.*)$", text, re.M)
    out["date"] = m.group(1).strip() if m else ""
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 6 and re.fullmatch(r"R-\d+", cells[0]):
            out["rows"][cells[0]] = {"title": cells[1], "now": cells[2], "scope": cells[3],
                                     "decision": cells[4].lower(), "comment": "|".join(cells[5:]).strip()}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ratings", nargs="?", default="outputs/risk-ratings.json")
    ap.add_argument("--rules", default="outputs/rules.json")
    ap.add_argument("--analytics", default="outputs/analytics.json")
    ap.add_argument("--history", default="outputs/history.json")
    ap.add_argument("--comments", default="outputs/auditor-comments.md")
    ap.add_argument("--out-dir", default="outputs")
    a = ap.parse_args()

    fails, warns = [], []
    for p in (a.ratings, a.rules, a.analytics, a.history):
        if not Path(p).exists():
            print(f"FAIL  input missing: {p}")
            return 1
    try:
        R = json.loads(Path(a.ratings).read_text())
    except json.JSONDecodeError as e:
        print(f"FAIL  {a.ratings} is not valid JSON: {e}")
        return 1
    rules = {r["rule_id"]: r for r in json.loads(Path(a.rules).read_text())["rules"]}
    an = json.loads(Path(a.analytics).read_text())
    H = json.loads(Path(a.history).read_text())
    hidx = history_index(H)
    sm = H.get("scoring_method") or {}
    usable = bool(sm.get("usable"))
    out_dir = Path(a.out_dir)
    comments_path = Path(a.comments)
    dec = read_comments(comments_path)
    decided = OrderedDict((k, v) for k, v in dec["rows"].items() if v["decision"])

    # ---- scoring method
    L_LABEL = {x["score"]: x["label"] for x in sm.get("likelihood_scale") or []} if usable else FALLBACK_L
    I_LABEL = {x["score"]: x["label"] for x in sm.get("impact_scale") or []} if usable else FALLBACK_L
    # history.json is written by an agent, so accept the shapes it has used:
    # matrix as rows of cells or as rows keyed by impact; bands with numeric
    # bounds or a printed range ("15-25", "Up to 3"); thresholds as values or quotes.
    MATRIX = {}
    comb = sm.get("combination") or {}
    for row in comb.get("matrix") or []:
        for c in row.get("cells") or []:
            MATRIX[(int(c["likelihood"]), int(row["impact"]))] = c.get("label", "")
    for imp, row in (comb.get("matrix_rows_by_impact") or {}).items():
        for li, lab in enumerate(row.get("labels") or [], 1):
            MATRIX[(li, int(imp))] = lab
    BANDS = []
    for b in sm.get("bands") or []:
        lo, hi = b.get("score_min"), b.get("score_max")
        rng = str(b.get("score_range") or b.get("printed_range") or "")
        nums = [int(x) for x in re.findall(r"\d+", rng)]
        if lo is None and nums:
            lo, hi = (1, nums[0]) if re.search(r"up to", rng, re.I) or len(nums) == 1 else (nums[0], nums[1])
        level = re.sub(r"\s*\(.*\)\s*$", "", str(b.get("level", ""))).strip()
        if lo is not None:
            BANDS.append({"level": level, "score_min": int(lo), "score_max": int(hi if hi is not None else 25)})
    crt = sm.get("corporate_register_threshold") or {}

    def first_int(*vals):
        for v in vals:
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                return int(v)
            m = re.search(r"\d+", str(v or ""))
            if v and m:
                return int(m.group())
        return None
    fig4 = first_int((crt.get("figure_4") or {}).get("value"), crt.get("figure_4_score"),
                     crt.get("figure_4_text"), (crt.get("figure_4") or {}).get("quote"))
    tab4 = first_int((crt.get("table_4") or {}).get("value"), crt.get("table_4_score"))
    if tab4 is None:
        tab4 = min((b["score_min"] for b in BANDS if b["level"].lower() == "extreme"), default=None)

    def band_for(score):
        for b in BANDS:
            if b["score_min"] <= score <= b["score_max"]:
                return b["level"]
        return "no band in Table 4"

    def label_for(l, i):
        if (l, i) in MATRIX:
            return MATRIX[(l, i)]
        s = l * i
        return "Extreme" if s >= 15 else "High" if s >= 8 else "Moderate" if s >= 4 else "Low"

    # ---- citation helpers
    def resolve(text, where, record=True):
        ok = 0
        for kind, ref in CITE_RE.findall(text or ""):
            ref = ref.strip()
            if kind == "rule":
                if ref in rules: ok += 1
                elif record: fails.append(f"{where}: unknown rule {ref}")
            elif kind == "metric":
                found, val = jpath(an, ref)
                if found and not isinstance(val, (dict, list)): ok += 1
                elif record: fails.append(f"{where}: metric {ref} " + ("is not a scalar" if found else "not found in analytics.json"))
            else:
                if ref.startswith("$"):
                    found, _ = jpath(H, ref)
                else:
                    found = ref in hidx
                if found: ok += 1
                elif record: fails.append(f"{where}: history item {ref} not found in history.json")
        return ok

    def fill(text, where):
        def sub(m):
            found, val = jpath(an, m.group(1))
            if not found or isinstance(val, (dict, list)):
                fails.append(f"{where}: placeholder not resolvable {m.group(1)}")
                return "«unresolved»"
            return fmt(val)
        out = PH_RE.sub(sub, text or "")
        stripped = CITE_RE.sub("", PH_RE.sub("", text or ""))
        if NUM_RE.search(stripped):
            warns.append(f"{where}: figure typed in prose; use a {{{{$.path}}}} placeholder: {stripped[:70]!r}")
        return out

    def show_cites(text):
        """Render [rule:CPR-01] etc. as plain references for reading."""
        return CITE_RE.sub(lambda m: f"[{m.group(2).strip()}]", text or "")

    # ---- validate risks
    kept, dropped = [], []
    seen = set()
    for i, r in enumerate(R.get("risks") or []):
        rid = r.get("id") or f"#{i + 1}"
        if not re.fullmatch(r"R-\d+", rid):
            fails.append(f"{rid}: id must look like R-01")
        if rid in seen:
            fails.append(f"{rid}: duplicate id")
        seen.add(rid)
        bad = False
        for part in ("likelihood", "impact"):
            sc = (r.get(part) or {}).get("score")
            if not isinstance(sc, int) or isinstance(sc, bool) or not 1 <= sc <= 5:
                fails.append(f"{rid}.{part}: score must be an integer 1-5, got {sc!r}")
                bad = True
        n_l = resolve((r.get("likelihood") or {}).get("justification"), f"{rid}.likelihood", record=False)
        n_i = resolve((r.get("impact") or {}).get("justification"), f"{rid}.impact", record=False)
        if n_l == 0 or n_i == 0:  # dropped and listed, not failed
            which = " and ".join(p for p, n in (("likelihood", n_l), ("impact", n_i)) if n == 0)
            dropped.append({"id": rid, "title": r.get("title", ""), "reason": f"no resolvable citation in the {which} justification"})
            continue
        resolve((r.get("likelihood") or {}).get("justification"), f"{rid}.likelihood")
        resolve((r.get("impact") or {}).get("justification"), f"{rid}.impact")
        if bad:
            continue
        resolve(r.get("statement"), f"{rid}.statement")
        for ev in r.get("evidence") or []:
            resolve(f"[{ev}]", f"{rid}.evidence")
        up = r.get("repeat_uplift")
        if up:
            ref = (up.get("cites") or "").split(":", 1)[-1].strip()
            item = hidx.get(ref)
            if not item:
                fails.append(f"{rid}.repeat_uplift: cites {up.get('cites')!r}, which is not an audit in history.json")
            elif not ADVERSE.search(f"{item.get('opinion') or ''} {item.get('implementation_opinion') or ''}"):
                fails.append(f"{rid}.repeat_uplift: {ref} has opinion {item.get('opinion')!r}, not an adverse one")
            resolve(up.get("justification"), f"{rid}.repeat_uplift")
        kept.append(r)

    # ---- render text
    rendered = []
    for r in kept:
        rid = r["id"]
        L, I = r["likelihood"]["score"], r["impact"]["score"]
        s = L * I
        rendered.append({
            "id": rid, "r": r, "L": L, "I": I, "score": s,
            "label": label_for(L, I), "band": band_for(s),
            "fig4": ("yes" if fig4 is not None and s >= fig4 else "no") if fig4 is not None else "n/a",
            "scope": "in" if r.get("recommend_in_scope", True) else "out",
            "title": fill(r.get("title", ""), f"{rid}.title"),
            "statement": fill(r.get("statement", ""), f"{rid}.statement"),
            "lj": fill(r["likelihood"].get("justification", ""), f"{rid}.likelihood"),
            "ij": fill(r["impact"].get("justification", ""), f"{rid}.impact"),
            "focus": fill(r.get("proposed_focus", ""), f"{rid}.proposed_focus"),
            "scope_reason": fill(r.get("scope_reason", ""), f"{rid}.scope_reason"),
            "uplift": fill((r.get("repeat_uplift") or {}).get("justification", ""), f"{rid}.repeat_uplift") if r.get("repeat_uplift") else "",
        })

    # ---- revision checks
    versions = out_dir / ".register-versions"
    rev_block = R.get("revision")
    rev_no = None
    snap_now = {x["id"]: {"title": x["r"].get("title", ""), "statement": x["r"].get("statement", ""),
                          "L": x["L"], "I": x["I"], "scope": x["scope"],
                          "lj": x["r"]["likelihood"].get("justification", ""),
                          "ij": x["r"]["impact"].get("justification", "")} for x in rendered}
    excluded_ids = {x.get("id"): x for x in R.get("excluded") or [] if x.get("id")}
    applied = OrderedDict()
    if decided:
        bad_dec = [k for k, v in decided.items() if v["decision"] not in DECISIONS]
        if bad_dec:
            fails.append(f"decisions must be approve, amend or reject: {', '.join(bad_dec)}")
        if not rev_block:
            fails.append("auditor-comments.md holds decisions but risk-ratings.json has no revision block")
        else:
            rev_no = rev_block.get("number")
            if not isinstance(rev_no, int) or rev_no < 1:
                fails.append(f"revision.number must be an integer >= 1, got {rev_no!r}")
                rev_no = None
        changed = {c.get("id"): c.get("as") for c in (rev_block or {}).get("changed") or []}
        prev_path = versions / f"v{(rev_no or 1) - 1}.json"
        prev = json.loads(prev_path.read_text()) if prev_path.exists() else None
        if rev_no and prev is None:
            fails.append(f"no snapshot of the previous version ({prev_path}); build the first run before a revision")
        prev = prev or {"risks": {}, "excluded_ids": []}
        for rid, v in decided.items():
            d = v["decision"]
            if rid not in prev["risks"] and rid in prev.get("excluded_ids", []):
                applied[rid] = "rejected earlier; stays excluded"
                continue
            if d == "approve":
                if rid not in snap_now:
                    fails.append(f"{rid}: approved by the auditor but missing from the register")
                elif rid in changed:
                    fails.append(f"{rid}: approved, but the revision block lists it as {changed[rid]}")
                applied[rid] = "kept as rated"
            elif d == "amend":
                if rid not in snap_now:
                    fails.append(f"{rid}: amended by the auditor but missing from the register")
                if changed.get(rid) != "amended":
                    fails.append(f"{rid}: amend decision not applied (revision block must list it as amended)")
                over = any(x["id"] == rid and x["r"].get("auditor_override") for x in rendered)
                applied[rid] = "amended" + (" (auditor override)" if over else "")
            elif d == "reject":
                if rid in snap_now:
                    fails.append(f"{rid}: rejected by the auditor but still in the register")
                if rid not in excluded_ids:
                    fails.append(f"{rid}: rejected but not listed in excluded with its id")
                if changed.get(rid) != "rejected":
                    fails.append(f"{rid}: reject decision not applied (revision block must list it as rejected)")
                applied[rid] = "rejected; moved to excluded"
        for rid, how in changed.items():
            if rid not in decided:
                fails.append(f"{rid}: listed as {how} in the revision block, but the auditor recorded no decision")
        for rid, old in prev["risks"].items():
            if rid in decided and decided[rid]["decision"] in ("amend", "reject"):
                continue
            if rid not in snap_now:
                fails.append(f"{rid}: was in the previous version and has gone without a reject decision")
            elif snap_now[rid] != old:
                diff = [k for k in old if snap_now[rid].get(k) != old[k]]
                fails.append(f"{rid}: changed ({', '.join(diff)}) although the auditor did not ask for it")
        for rid in snap_now:
            if prev["risks"] and rid not in prev["risks"]:
                fails.append(f"{rid}: new risk in a revision; the auditor did not ask for it")
    elif rev_block:
        fails.append("risk-ratings.json has a revision block but auditor-comments.md records no decision")

    # ---- header notes
    today = R.get("generated_at") or str(datetime.date.today())
    notes = []
    if usable:
        notes.append(f"Scale: the council's own method from `{sm.get('source_document', 'the Risk Management Strategy')}` "
                     f"(likelihood 1 {L_LABEL.get(1, '')} to 5 {L_LABEL.get(5, '')}; impact 1 {I_LABEL.get(1, '')} to 5 {I_LABEL.get(5, '')}). "
                     "Score = likelihood × impact. Matrix label from Figure 1; band from Table 4.")
    else:
        notes.append("Scale: FALLBACK. history.json reports no usable council scoring method, so 1-5 Very low to Very high is used.")
    if fig4 is not None and tab4 is not None and fig4 != tab4:
        notes.append(f"Conflict in the scoring method, not resolved here: Table 4 adds risks scoring {tab4} or more to the Corporate Risk "
                     f"Register; Figure 4 says {fig4} or above. Bands use Table 4; the Fig. 4 column marks risks that meet the Figure 4 rule.")
    names = sorted({lab for lab in MATRIX.values()} - {b.get("level") for b in BANDS})
    if names:
        notes.append(f"Naming: the Figure 1 matrix uses {', '.join(names)} where Table 4 names its bands "
                     f"{', '.join(b.get('level', '') for b in BANDS)}; both are shown.")

    # ---- register
    md = ["# Procurement audit planning: risk register\n"]
    if rev_no:
        md.append(f"*Status: REVISION {rev_no} for auditor sign-off.*\n")
        ch = ", ".join(f"{c.get('id')} ({c.get('as')})" for c in (rev_block or {}).get("changed") or []) or "none"
        md.append(f"*Revision {rev_no}, following auditor comments dated {dec['date'] or 'undated'}"
                  f"{' by ' + dec['reviewer'] if dec['reviewer'] else ''}. Changed: {ch}.*\n")
    else:
        md.append("*Status: DRAFT for auditor approval. Nothing here is in scope until the auditor decides.*\n")
    md.append(f"*Generated {today} by `build_register.py` from `risk-ratings.json`, `rules.json`, `analytics.json` and `history.json`.*\n")
    md.append("**Indicators, not findings.** Each risk describes a pattern in public data to investigate. "
              "Nothing here asserts wrongdoing by the council, a department, an officer or a supplier.\n")
    for n in notes:
        md.append(f"- {n}")
    md.append("\n## Summary\n")
    fig4_head = f"Fig. 4 (≥ {fig4})" if fig4 is not None else "Fig. 4"
    md.append(f"| ID | Risk | L | I | Score | Matrix label | Band (Table 4) | {fig4_head} | Scope |")
    md.append("|---|---|---|---|---|---|---|---|---|")
    for x in rendered:
        md.append(f"| {x['id']} | {cell(x['title'])} | {x['L']} | {x['I']} | {x['score']} | {x['label']} | {x['band']} | {x['fig4']} | {x['scope']} |")
    md.append("\n## Risks\n")
    for x in rendered:
        r = x["r"]
        md.append(f"### {x['id']}: {x['title']}\n")
        md.append(f"{show_cites(x['statement'])}\n")
        flag = " *Auditor override.*" if r.get("auditor_override") else ""
        md.append(f"**Likelihood {x['L']} ({L_LABEL.get(x['L'], '')}).** {show_cites(x['lj'])}{flag}\n")
        if x["uplift"]:
            md.append(f"**Repeat-finding uplift (+1 included above).** {show_cites(x['uplift'])}\n")
        md.append(f"**Impact {x['I']} ({I_LABEL.get(x['I'], '')}).** {show_cites(x['ij'])}\n")
        md.append(f"**Score {x['score']}: {x['label']} (matrix); {x['band']} (Table 4).**\n")
        md.append("**Evidence**\n")
        for ev in r.get("evidence") or []:
            kind, ref = ev.split(":", 1) if ":" in ev else ("", ev)
            ref = ref.strip()
            if kind == "rule" and ref in rules:
                q = re.sub(r"\s+", " ", rules[ref].get("verbatim_quote", "")).strip()
                exc = q if len(q) <= 140 else q[:140].rstrip() + "…"
                clause = str(rules[ref].get("clause", "")).replace(":", " ")
                md.append(f'- [rule:{ref}] clause {clause}: "{exc}"')
            elif kind == "metric":
                found, val = jpath(an, ref)
                md.append(f"- [metric:{ref}] {fmt(val) if found else '«unresolved»'}")
            elif kind == "history":
                it = hidx.get(ref) or {}
                what = it.get("audit_title") or it.get("theme") or it.get("what") or it.get("item") or ref
                op = f": {it['opinion']}" if it.get("opinion") else ""
                src = f" ({it.get('source', '')}, p. {it.get('pdf_page', '')})" if it.get("source") else ""
                md.append(f"- [history:{ref}] {cell(what)}{op}{src}")
            else:
                md.append(f"- {ev}")
        md.append(f"\n**Proposed focus.** {show_cites(x['focus'])}\n")
        md.append(f"**Recommended scope: {x['scope']}.** {show_cites(x['scope_reason'])}"
                  + (f" Sample source: `analytics-full/{r['sample_source']}`." if r.get("sample_source") else "") + "\n")
    md.append("## Excluded\n")
    if not (R.get("excluded") or dropped):
        md.append("None.\n")
    for x in R.get("excluded") or []:
        tag = f"{x['id']}: " if x.get("id") else ""
        md.append(f"- {tag}{x.get('theme', '')}: {x.get('reason', '')}")
    for x in dropped:
        md.append(f"- {x['id']}: {x['title']}: excluded by validation, {x['reason']}")
    md.append("\n## Auditor decisions\n")
    if not decided:
        md.append("No decisions recorded yet. The auditor records approve, amend or reject for each risk in "
                  "`outputs/auditor-comments.md`; the risk-assessor is then re-run to produce a revision.")
    else:
        md.append(f"Decisions by {dec['reviewer'] or 'an unnamed reviewer'}, dated {dec['date'] or 'undated'}.\n")
        md.append("| ID | Decision | Applied as | Comment |\n|---|---|---|---|")
        for rid, v in decided.items():
            md.append(f"| {rid} | {v['decision']} | {applied.get(rid, '')} | {cell(v['comment'])} |")
        pending = [x["id"] for x in rendered if x["id"] not in decided]
        if pending:
            md.append(f"\nNo decision yet: {', '.join(pending)}.")

    # ---- write (the register and template are written even with failures, so the agent can read them)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "risk-register.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    rows = OrderedDict()
    for x in rendered:
        old = dec["rows"].get(x["id"], {})
        rows[x["id"]] = [x["id"], cell(x["title"]), f"{x['L']} × {x['I']} = {x['score']}", x["scope"],
                         old.get("decision", ""), cell(old.get("comment", ""))]
    for rid, v in dec["rows"].items():  # decisions on risks no longer in the register (e.g. rejected) stay on record
        if rid not in rows and v["decision"]:
            rows[rid] = [rid, cell(v["title"]), v["now"], "excluded", v["decision"], cell(v["comment"])]
    cm = ["# Auditor comments: risk register gate\n", f"Reviewer: {dec['reviewer']}", f"Date: {dec['date']}\n",
          "For each risk write approve, amend (say what to change) or reject (say why) in Decision. "
          "A blank Decision means no decision yet. Re-run the risk-assessor to apply the decisions.\n",
          "| ID | Risk | Now | Scope now | Decision | Comment |", "|---|---|---|---|---|---|"]
    cm += ["| " + " | ".join(r) + " |" for r in rows.values()]
    comments_path.write_text("\n".join(cm) + "\n", encoding="utf-8")

    if not fails:
        versions.mkdir(parents=True, exist_ok=True)
        (versions / f"v{rev_no or 0}.json").write_text(json.dumps(
            {"risks": snap_now, "excluded_ids": sorted(set(excluded_ids) | {d["id"] for d in dropped})}, indent=1) + "\n")

    for w in warns: print("WARN ", w)
    for f in fails: print("FAIL ", f)
    print(f"\nrisks kept: {len(rendered)}, excluded by validation: {len(dropped)}, warnings: {len(warns)}, failures: {len(fails)}")
    print(f"written: {out_dir / 'risk-register.md'}" + (f" (revision {rev_no})" if rev_no else " (first run)"))
    n_dec = sum(1 for x in rendered if dec["rows"].get(x["id"], {}).get("decision"))
    print(f"written: {comments_path} ({len(rendered)} risks, {n_dec} with a decision already recorded"
          + (f"; revision {rev_no}, {len((rev_block or {}).get('changed') or [])} changed)" if rev_no else ")"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
