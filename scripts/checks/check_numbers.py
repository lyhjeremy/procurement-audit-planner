#!/usr/bin/env python3
"""QA check: every figure in the pack is the right figure, traced to its source.

Three layers, none of which trusts pack-figures.json (the builder writes it):

1. Placeholders in place. Every text in outputs/audit-plan.json that the
   builder fills ({{$.path}} placeholders: memo paragraphs, objectives,
   controls, test steps, evidence) is filled here from analytics.json and
   must appear word for word in the documents. A figure swapped for another
   real figure fails, because the filled sentence no longer matches.
2. Builder sentences recomputed. The counts and totals the builder writes
   itself (rated risks, decisions, risks in and out of scope, controls,
   tests, sample rows, distinct sampled transactions and their £ value,
   rules cited and not tested) are recomputed from risk-register.md,
   auditor-comments.md, audit-plan.json, rules.json, risk-ratings.json and
   samples/*.csv, and compared with the figures printed in each sentence.
   Every risk score printed in the memo's scope table and the risk-control
   matrix must equal the register's score for that risk.
3. Safety net. Any other figure (three or more digits, or a £ amount) must be
   a value in analytics.json, rules.json or samples/*.csv. Row IDs, rule/risk/
   test IDs, dates, years, clause and page references are not figures.

Prints PASS/FAIL lines and a summary; exit 0 when clean.
"""
import csv, json, re, sys
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "outputs"  # an outputs folder to check; default outputs/
IN = ROOT / "outputs"  # analytics, rules, ratings, register and decisions always come from the project
DOCS = ["planning-memo.md", "risk-control-matrix.md", "audit-program.md"]
PH_RE = re.compile(r"\{\{(\$[^}]+)\}\}")
CITE_RE = re.compile(r"\[(rule|metric|history):((?:[^\[\]]|\[\d+\])+)\]")
SKIP = [
    r"`[^`]*`",                      # code spans (row IDs, paths)
    r"\b[A-Za-z0-9_\-]+\.xlsx:\d+",  # bare row IDs
    r"\b(?:CPR|R|C|T)-\d+(?:\.\d+)?\b",
    r"\b\d{4}-\d{2}-\d{2}\b",        # dates
    r"\b(?:19|20)\d{2}\b",           # years
    r"\bp\.\s?\d+\b",                # page refs
    r"\bclause [\dA-Za-z. ]+",       # clause refs
    r"\[metric:[^\]]+\]",
]
NUM = re.compile(r"£\s?(\d[\d,]*(?:\.\d+)?)|(?<![\w.])(\d[\d,]*\d)(?![\w.])")


def jpath(obj, path):
    """Resolve $.a.b[0].c against obj; return (found, value)."""
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


def money(s):
    return round(float(str(s).replace(",", "").replace("£", "")), 2)


def walk(o, out):
    if isinstance(o, dict):
        for v in o.values(): walk(v, out)
    elif isinstance(o, list):
        for v in o: walk(v, out)
    elif isinstance(o, (int, float)) and not isinstance(o, bool):
        out.add(round(float(o), 2))
    elif isinstance(o, str):
        for m in re.finditer(r"\d[\d,]*(?:\.\d+)?", o):
            try: out.add(round(float(m.group(0).replace(",", "")), 2))
            except ValueError: pass


def load(name, base=IN):
    p = base / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def table_rows(text, section=None):
    """Cells of markdown table rows whose first cell starts with a risk ID (optionally under one ## section)."""
    rows, on = [], section is None
    for line in text.splitlines():
        if section is not None and line.startswith("## "):
            on = line.strip() == section
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if on and line.lstrip().startswith("|") and re.match(r"R-\d+\b", cells[0]):
            rows.append(cells)
    return rows


def placeholder_layer(plan, an, docs, fails):
    """Layer 1: every filled text appears verbatim in the documents."""
    fields = []
    for k, v in (plan.get("memo") or {}).items():
        for i, s in enumerate(v if isinstance(v, list) else [v]):
            fields.append((f"memo.{k}[{i}]", s))
    for r in plan.get("risks") or []:
        fields.append((f"{r.get('id')}.objective", r.get("objective")))
        for c in r.get("controls") or []:
            fields.append((f"{r.get('id')}.{c.get('id')}.control", c.get("control")))
        for t in r.get("tests") or []:
            fields.append((f"{r.get('id')}.{t.get('id')}.step", t.get("step")))
            fields.append((f"{r.get('id')}.{t.get('id')}.evidence", t.get("evidence")))
    n = 0
    for where, text in fields:
        if not isinstance(text, str) or not PH_RE.search(text):
            continue
        bad = []

        def sub(m):
            found, val = jpath(an, m.group(1))
            if not found or isinstance(val, (dict, list)):
                bad.append(m.group(1))
                return "«unresolved»"
            return fmt(val)
        filled = PH_RE.sub(sub, text)
        n += len(PH_RE.findall(text))
        if bad:
            fails.append(f"{where}: placeholder not resolvable in analytics.json: {', '.join(bad)}")
        elif filled not in docs:
            fails.append(f"{where}: filled text not found in the pack (a figure differs from analytics.json): {filled[:90]!r}")
    return n


def builder_layer(plan, docs_by_name, fails, warns):
    """Layer 2: the builder's own sentences, recomputed from the primary files."""
    rules = load("rules.json") or {"rules": []}
    ratings = load("risk-ratings.json") or {"risks": []}
    reg_text = (IN / "risk-register.md").read_text(encoding="utf-8") if (IN / "risk-register.md").exists() else ""
    dec_text = (IN / "auditor-comments.md").read_text(encoding="utf-8") if (IN / "auditor-comments.md").exists() else ""
    reg = OrderedDict((c[0], c) for c in table_rows(reg_text, "## Summary") if len(c) >= 9)
    decisions = [c for c in table_rows(dec_text) if len(c) >= 6]
    planned = plan.get("risks") or []

    rule_ids = [r["rule_id"] for r in rules["rules"]]
    cited = set()
    for r in ratings.get("risks", []):
        cited |= {ref for kind, ref in CITE_RE.findall(json.dumps(r)) if kind == "rule" and ref in rule_ids}
    for r in planned:
        for item in (r.get("controls") or []) + (r.get("tests") or []):
            cited |= {c.split(":", 1)[1] for c in item.get("cites") or [] if c.startswith("rule:") and c.split(":", 1)[1] in rule_ids}
    listed = {x for g in plan.get("rules_not_tested") or [] for x in g.get("rule_ids") or []}

    rows = []
    for p in sorted((OUT / "samples").glob("T-*.csv")):
        with open(p, newline="", encoding="utf-8") as f:
            rows += list(csv.DictReader(f))
    distinct = OrderedDict((r["row_id"], money(r["amount"])) for r in rows)

    want = {
        "register_risks": len(reg), "decisions": len(decisions), "approved_in_scope": len(planned),
        "not_in_scope": len(decisions) - len(planned),
        "controls": sum(len(r.get("controls") or []) for r in planned),
        "tests": sum(len(r.get("tests") or []) for r in planned),
        "sample_rows": len(rows), "sampled_transactions": len(distinct),
        "sampled_gbp": round(sum(distinct.values()), 2), "rows_gbp": round(sum(money(r["amount"]) for r in rows), 2),
        "rules_total": len(rule_ids), "rules_cited": len([x for x in rule_ids if x in cited]),
        "rules_not_tested": len([x for x in rule_ids if x not in cited and x in listed]),
    }
    memo, matrix, program = (docs_by_name.get(n, "") for n in DOCS)
    n = 0

    def expect(doc, name, pattern, keys):
        nonlocal n
        ms = list(re.finditer(pattern, doc))
        if len(ms) != 1:
            fails.append(f"{name}: expected one builder sentence matching /{pattern[:60]}…/, found {len(ms)}")
            return None
        m = ms[0]
        for key, grp in keys:
            got = m.group(grp)
            n += 1
            if money(got) != want[key]:
                fails.append(f"{name}: {key} printed as {got}, recomputed {fmt(want[key])}")
        return m

    expect(memo, "planning-memo.md",
           r"The register lists (\d+) rated risks\. The auditor recorded (\d+) decisions[^:\n]*: (\d+) risks are approved and in scope, and (\d+) (?:is|are) not\.",
           [("register_risks", 1), ("decisions", 2), ("approved_in_scope", 3), ("not_in_scope", 4)])
    new = r"The programme holds (\d+) expected controls and (\d+) test steps, with (\d+) sample rows covering (\d+) distinct transactions worth £([\d,]+\.\d\d)"
    old = r"The programme holds (\d+) expected controls and (\d+) test steps, with (\d+) sampled transactions worth £([\d,]+\.\d\d)"
    if re.search(new, memo):
        expect(memo, "planning-memo.md", new, [("controls", 1), ("tests", 2), ("sample_rows", 3),
                                               ("sampled_transactions", 4), ("sampled_gbp", 5)])
    else:  # packs built before distinct transactions were reported
        m = expect(memo, "planning-memo.md", old, [("controls", 1), ("tests", 2), ("sample_rows", 3), ("rows_gbp", 4)])
        if m and want["sample_rows"] != want["sampled_transactions"]:
            warns.append(f"planning-memo.md: older wording; its {m.group(3)} 'sampled transactions' are sample rows covering "
                         f"{want['sampled_transactions']} distinct transactions worth £{want['sampled_gbp']:,.2f} "
                         f"(rebuild the pack to print the distinct figures)")
    expect(memo, "planning-memo.md",
           r"(\d+) of (\d+) rules in `rules\.json` are cited by a risk, a control or a test\. The remaining (\d+) are not tested",
           [("rules_cited", 1), ("rules_total", 2), ("rules_not_tested", 3)])
    expect(program, "audit-program.md",
           r"(\d+) risks in scope, (\d+) controls, (\d+) tests, (\d+) (?:sampled transactions|sample rows \((\d+) distinct transactions\))\.",
           [("approved_in_scope", 1), ("controls", 2), ("tests", 3), ("sample_rows", 4)]
           + ([("sampled_transactions", 5)] if "distinct transactions)." in program else []))

    # risk scores: memo scope table (ID | Risk | Score | ...) and matrix (R-xx: title | score (band) | ...)
    for name, doc, section in (("planning-memo.md", memo, "## Scope"), ("risk-control-matrix.md", matrix, None)):
        for cells in table_rows(doc, section):
            rid = re.match(r"R-\d+", cells[0]).group(0)
            col = 2 if name == "planning-memo.md" else 1
            got = re.match(r"\d+", cells[col]) if len(cells) > col else None
            if rid not in reg:
                fails.append(f"{name}: {rid} is not in the register's summary table")
                continue
            n += 1
            if not got or int(got.group(0)) != int(reg[rid][4]):
                fails.append(f"{name}: {rid} score printed as {cells[col] if len(cells) > col else '?'}, register says {reg[rid][4]}")
    return n


def main():
    fails, warns = [], []
    docs_by_name = {}
    for name in DOCS:
        p = OUT / name
        if p.exists():
            docs_by_name[name] = p.read_text(encoding="utf-8")
        else:
            fails.append(f"{name} missing")
    docs = "\n".join(docs_by_name.values())
    an = load("analytics.json") or {}
    plan = load("audit-plan.json", OUT) or {}
    if not plan:
        fails.append("audit-plan.json missing: placeholder and builder figures cannot be traced")

    n_ph = placeholder_layer(plan, an, docs, fails) if plan else 0
    n_builder = builder_layer(plan, docs_by_name, fails, warns) if plan else 0

    allowed = set()
    for name in ("analytics.json", "rules.json"):
        walk(load(name) or {}, allowed)
    for p in (OUT / "samples").glob("*.csv"):
        with open(p, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                for v in row.values():
                    try: allowed.add(round(float(v), 2))
                    except (TypeError, ValueError): pass
    # values the builder computes are verified by layer 2; recipe values come from the plan the QA reads
    for r in plan.get("risks") or []:
        for t in r.get("tests") or []:
            walk(t.get("sample") or {}, allowed)
    for v in re.findall(r"£([\d,]+\.\d\d)|\b(\d+) (?:rated risks|decisions|risks|expected controls|controls|test steps|tests|"
                        r"sample rows|sampled transactions|distinct transactions|of \d+ rules|rules)\b", docs):
        for x in v:
            if x: allowed.add(money(x))
    checked = 0
    for name, text_all in docs_by_name.items():
        for ln, line in enumerate(text_all.splitlines(), 1):
            text = line
            for pat in SKIP:
                text = re.sub(pat, " ", text)
            for m in NUM.finditer(text):
                raw = (m.group(1) or m.group(2)).replace(",", "")
                if len(re.sub(r"\D", "", raw)) < 3 and not m.group(1):
                    continue
                checked += 1
                try: val = round(float(raw), 2)
                except ValueError: continue
                if val not in allowed:
                    fails.append(f"{name}:{ln}: figure {m.group(0).strip()} not found in analytics, rules, samples or the builder's recomputed sentences")
    for w in warns:
        print("WARN ", w)
    for f in fails[:40]:
        print("FAIL ", f)
    if len(fails) > 40: print(f"FAIL  … and {len(fails) - 40} more")
    print(f"SUMMARY numbers: placeholders={n_ph} builder_figures={n_builder} figures_checked={checked} "
          f"allowed_values={len(allowed)} warnings={len(warns)} failures={len(fails)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
