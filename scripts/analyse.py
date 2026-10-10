"""Run the spend-analyst tests on outputs/analytics-full/spend-clean.csv.

Thresholds are read from outputs/rules.json; none is typed here.
Writes outputs/analytics.json and CSVs under outputs/analytics-full/.
"""
import difflib
import json
import os
import re
import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FULL = os.path.join(ROOT, "outputs", "analytics-full")
RULES = os.path.join(ROOT, "outputs", "rules.json")

# Method parameters from the spend-analyst agent file (not rule thresholds).
CLUSTER_BAND_LOW = 0.9
COMPARATOR_HIGH = 1.1
BASELINE = (0.5, 1.5)
SPLIT_WINDOW_DAYS = 30
DUP_WINDOW_DAYS = 7
NEAR_RATIO = 0.85
SPEND_VS_AWARD_RATIO = 1.25
TOP = 20
COMPETITION_RE = re.compile(r"tender|invitations? to quote|at least (three|five)", re.I)
QUOTE_OR_TENDER_RE = re.compile(r"quote|tender", re.I)
GENERIC = set("""AND OF THE SERVICES SERVICE GROUP CARE COMPANY HOMES HOME HOUSE UNIVERSITY COUNCIL TRUST
SOLUTIONS CONSULTANCY CONSULTING ASSOCIATES PARTNERSHIP NETWORK CENTRE CENTER TRAVEL CARS COACHES TAXIS
CONSTRUCTION HEALTHCARE HEALTH SCHOOL SCHOOLS EDUCATION SUPPORT LIVING CHILDREN CHILDRENS SEN BERKSHIRE
WEST SOUTH NORTH EAST READING NEWBURY THATCHAM HUNGERFORD SOUTHERN SYSTEMS SOFTWARE HOUSING SECURITY
CLEANING FOSTERING COMMUNITY BUSINESS MANAGEMENT FACILITIES SUPPLIES CATERING TRANSPORT ENGINEERING HIRE
PROPERTY PROPERTIES VALLEY""".split())

CAVEAT = ("contracts.csv holds published notices, not a contract register. It holds awards published on "
          "Contracts Finder in roughly the last five years. A contract awarded earlier (e.g. long-running waste "
          "or highways contracts), one advertised only on Find a Tender, a framework call-off recorded under "
          "another buyer, or an exempt placement will have no notice here. \"No notice found\" is therefore an "
          "indicator to check against the council's contract register, never evidence of off-contract spend.")


def r2(x):
    return round(float(x), 2)


def load_rules():
    if not os.path.exists(RULES):
        print("STOP: outputs/rules.json missing")
        sys.exit(1)
    with open(RULES) as f:
        return json.load(f)


def rule_ids_for_clause(rules, clause):
    return [r["rule_id"] for r in rules["rules"] if r.get("clause") == clause]


def build_thresholds(rules):
    """Distinct numeric thresholds from threshold/approver/anti-avoidance rules.

    inclusive=True means a value equal to T is at or above the trigger (band below is amount < T).
    Taken from the threshold_low flag of competition-triggering rules starting at T, else any rule
    starting at T, else the negation of threshold_high_inclusive of rules ending at T.
    """
    acc = {}
    for r in rules["rules"]:
        if r.get("type") not in ("threshold", "approver", "anti-avoidance"):
            continue
        action = r.get("required_action") or ""
        comp = bool(COMPETITION_RE.search(action))
        qt = bool(QUOTE_OR_TENDER_RE.search(action))
        for side in ("low", "high"):
            v = r.get(f"threshold_{side}")
            if v is None:
                continue
            flag = r.get(f"threshold_{side}_inclusive")
            e = acc.setdefault(float(v), {"rule_ids": [], "low_comp": [], "low_any": [], "high_neg": [],
                                          "competition_triggering": False, "quote_or_tender_mentioned": False,
                                          "competition_rule_ids": []})
            e["rule_ids"].append(r["rule_id"])
            if side == "low":
                e["low_any"].append(flag)
                if comp:
                    e["low_comp"].append(flag)
                    e["competition_triggering"] = True
                    e["competition_rule_ids"].append(r["rule_id"])
                if qt:
                    e["quote_or_tender_mentioned"] = True
            else:
                e["high_neg"].append(None if flag is None else (not flag))
    out = []
    for v in sorted(acc):
        e = acc[v]
        src, flags = None, []
        for name in ("low_comp", "low_any", "high_neg"):
            flags = [f for f in e[name] if f is not None]
            if flags:
                src = name
                break
        inclusive = flags[0] if flags else True
        all_flags = [f for f in e["low_any"] + e["high_neg"] if f is not None]
        out.append({
            "value": v, "inclusive": bool(inclusive), "inclusive_source": src or "default_true",
            "inclusivity_conflict": len(set(all_flags)) > 1,
            "competition_triggering": e["competition_triggering"],
            "quote_or_tender_mentioned": e["quote_or_tender_mentioned"],
            "competition_rule_ids": sorted(set(e["competition_rule_ids"])),
            "rule_ids": sorted(set(e["rule_ids"])),
        })
    return out


def below(amount, t):
    """Amount that does not itself reach the trigger."""
    return amount < t["value"] if t["inclusive"] else amount <= t["value"]


def reaches(amount, t):
    return amount >= t["value"] if t["inclusive"] else amount > t["value"]


def tag_split(df, amount_col="Net amount"):
    g = df.groupby("tag")[amount_col].agg(["count", "sum"])
    return {k: {"rows": int(v["count"]), "gbp": r2(v["sum"])} for k, v in g.iterrows()}


# ---------------- matching ----------------

def dist_tokens(name):
    return frozenset(t for t in str(name).split() if t not in GENERIC and len(t) >= 3)


def match_suppliers(spend_sups, notice_sups):
    notice_set = set(notice_sups)
    notice_list = sorted(notice_set)
    spend_tok = {s: dist_tokens(s) for s in spend_sups}
    notice_tok = {n: dist_tokens(n) for n in notice_list}
    spend_tok_count, notice_tok_count = {}, {}
    for toks in spend_tok.values():
        for t in toks:
            spend_tok_count[t] = spend_tok_count.get(t, 0) + 1
    for toks in notice_tok.values():
        for t in toks:
            notice_tok_count[t] = notice_tok_count.get(t, 0) + 1
    rows = []
    for s in spend_sups:
        if s in notice_set:
            rows.append({"supplier_norm": s, "match_class": "exact", "candidate": s, "score": 1.0, "rule": "exact"})
            continue
        best, best_r = None, 0.0
        for n in notice_list:
            r = difflib.SequenceMatcher(None, s, n).ratio()
            if r > best_r:
                best, best_r = n, r
        if best is not None and best_r >= NEAR_RATIO:
            rows.append({"supplier_norm": s, "match_class": "near_ratio", "candidate": best,
                         "score": round(best_r, 3), "rule": f"SequenceMatcher ratio >= {NEAR_RATIO}"})
            continue
        st = spend_tok[s]
        hit = None
        for n in notice_list:
            nt = notice_tok[n]
            if not st or not nt:
                continue
            small, large = (st, nt) if len(st) <= len(nt) else (nt, st)
            if not small <= large:
                continue
            if len(small) >= 2:
                hit = (n, "distinctive token subset, >= 2 tokens")
                break
            (tok,) = tuple(small)
            if spend_tok_count.get(tok, 0) == 1 and notice_tok_count.get(tok, 0) == 1:
                hit = (n, "single distinctive token unique on both sides")
                break
        if hit:
            rows.append({"supplier_norm": s, "match_class": "near_contain", "candidate": hit[0],
                         "score": round(best_r, 3), "rule": hit[1]})
        else:
            rows.append({"supplier_norm": s, "match_class": "none", "candidate": "", "score": round(best_r, 3),
                         "rule": ""})
    return pd.DataFrame(rows)


# ---------------- tests ----------------

def test_threshold_clustering(df, thresholds):
    blocks, frames = [], []
    for t in thresholds:
        T = t["value"]
        lo = CLUSTER_BAND_LOW * T
        band = df[(df["Net amount"] >= lo) & below(df["Net amount"], t)]
        comp = df[reaches(df["Net amount"], t) & (df["Net amount"] < COMPARATOR_HIGH * T)]
        base = df[(df["Net amount"] >= BASELINE[0] * T) & (df["Net amount"] < BASELINE[1] * T)]
        sup = (band.groupby("supplier_norm")["Net amount"].agg(["count", "sum"])
               .sort_values(["count", "sum"], ascending=False).head(TOP))
        top = band.sort_values("Net amount", ascending=False).head(TOP)
        blocks.append({
            "threshold": T, "inclusive": t["inclusive"], "rule_ids": t["rule_ids"],
            "band": f"{CLUSTER_BAND_LOW} x T <= amount {'<' if t['inclusive'] else '<='} T",
            "description": f"payments within 10% below £{T:,.0f}",
            "band_count": int(len(band)), "band_gbp": r2(band["Net amount"].sum()),
            "comparator_band": f"amount {'>=' if t['inclusive'] else '>'} T and < {COMPARATOR_HIGH} x T",
            "comparator_count": int(len(comp)), "comparator_gbp": r2(comp["Net amount"].sum()),
            "baseline_band": f"{BASELINE[0]} x T <= amount < {BASELINE[1]} x T",
            "baseline_count": int(len(base)), "baseline_gbp": r2(base["Net amount"].sum()),
            "by_tag": tag_split(band),
            "supplier_concentration_top20": [{"supplier_norm": k, "payments": int(v["count"]), "gbp": r2(v["sum"])}
                                             for k, v in sup.iterrows()],
            "top20": [{"row_id": r.row_id, "supplier": r["Supplier name"], "amount": r2(r["Net amount"]),
                       "pay_date": r.pay_date, "service": r.Service, "narrative": r.Narrative, "tag": r.tag}
                      for _, r in top.iterrows()],
        })
        b = band.copy()
        b.insert(0, "threshold", T)
        frames.append(b)
    out = pd.concat(frames) if frames else pd.DataFrame()
    out.to_csv(os.path.join(FULL, "threshold-clustering.csv"), index=False)
    return {"parameters": {"band_low_factor": CLUSTER_BAND_LOW, "comparator_high_factor": COMPARATOR_HIGH,
                           "baseline_factors": list(BASELINE), "thresholds": [t["value"] for t in thresholds]},
            "rule_ids": sorted({i for t in thresholds for i in t["rule_ids"]}),
            "per_threshold": blocks, "full_list": "outputs/analytics-full/threshold-clustering.csv"}


def test_split_purchases(df, comp_thresholds, anti_ids):
    blocks, all_windows = [], []
    for t in comp_thresholds:
        T = t["value"]
        sub = df[below(df["Net amount"], t)].copy()
        sub["d"] = pd.to_datetime(sub["pay_date"])
        windows = []
        for sup, g in sub.groupby("supplier_norm"):
            if len(g) < 2:
                continue
            g = g.sort_values(["d", "row_id"])
            dates = g["d"].values
            amts = g["Net amount"].values
            best = None
            for i in range(len(g)):
                end = dates[i] + np.timedelta64(SPLIT_WINDOW_DAYS - 1, "D")
                m = (dates >= dates[i]) & (dates <= end)
                n = int(m.sum())
                tot = float(amts[m].sum())
                if n >= 2 and reaches(tot, t) and (best is None or tot > best[0]):
                    best = (tot, i, m)
            if best is None:
                continue
            tot, i, m = best
            w = g[m]
            tag_gbp = w.groupby("tag")["Net amount"].sum().sort_values(ascending=False)
            windows.append({
                "threshold": T, "supplier_norm": sup, "supplier": w["Supplier name"].iloc[0],
                "window_start": str(pd.Timestamp(dates[i]).date()),
                "window_end": str((pd.Timestamp(dates[i]) + pd.Timedelta(days=SPLIT_WINDOW_DAYS - 1)).date()),
                "n_payments": int(len(w)), "total_gbp": r2(tot),
                "distinct_amounts": int(w["Net amount"].round(2).nunique()),
                "services": "; ".join(sorted(w["Service"].astype(str).unique())),
                "tag": tag_gbp.index[0], "spans_tags": bool(len(tag_gbp) > 1),
                "row_ids": "; ".join(w["row_id"]),
            })
        wd = pd.DataFrame(windows)
        all_windows.append(wd)
        if wd.empty:
            blocks.append({"threshold": T, "windows": 0, "suppliers": 0, "gbp": 0.0, "by_tag": {}})
            continue
        by_tag = {k: {"windows": int(len(v)), "gbp": r2(v["total_gbp"].sum())} for k, v in wd.groupby("tag")}
        gp = wd[wd["tag"] == "general_procurement"].sort_values("total_gbp", ascending=False)
        pl = wd[wd["tag"] == "care_or_education_placement"].sort_values("total_gbp", ascending=False)
        cols = ["supplier", "window_start", "window_end", "n_payments", "total_gbp", "distinct_amounts",
                "services", "tag", "row_ids"]
        blocks.append({
            "threshold": T, "rule_ids": t["rule_ids"],
            "description": f"same supplier, >= 2 payments each below £{T:,.0f} within {SPLIT_WINDOW_DAYS} days, "
                           f"combined total reaching £{T:,.0f}",
            "windows": int(len(wd)), "suppliers": int(wd["supplier_norm"].nunique()), "gbp": r2(wd["total_gbp"].sum()),
            "by_tag": by_tag,
            "headline_general_procurement": {"windows": int(len(gp)), "gbp": r2(gp["total_gbp"].sum()),
                                             "top20": gp[cols].head(TOP).to_dict("records")},
            "care_or_education_placement": {"windows": int(len(pl)), "gbp": r2(pl["total_gbp"].sum()),
                                            "note": "periodic care fees legitimately recur",
                                            "top20": pl[cols].head(TOP).to_dict("records")},
            "top20_all": wd.sort_values("total_gbp", ascending=False)[cols].head(TOP).to_dict("records"),
        })
    out = pd.concat(all_windows) if all_windows else pd.DataFrame()
    out.to_csv(os.path.join(FULL, "split-purchases.csv"), index=False)
    return {"parameters": {"window_days": SPLIT_WINDOW_DAYS, "min_payments": 2,
                           "thresholds": [t["value"] for t in comp_thresholds],
                           "window_rule": "anchored on each payment, calendar dates anchor to anchor+29 days; "
                                          "one highest-total window kept per supplier per threshold",
                           "lower_bound_note": "payments of £500 or less are not published, so counts are lower bounds"},
            "rule_ids": sorted(set(anti_ids) | {i for t in comp_thresholds for i in t["rule_ids"]}),
            "per_threshold": blocks, "full_list": "outputs/analytics-full/split-purchases.csv"}


def supplier_table(df, factor):
    g = df.groupby("supplier_norm")
    tot = g["Net amount"].agg(["count", "sum"]).rename(columns={"count": "n_payments", "sum": "total_gbp"})
    tag_gbp = df.groupby(["supplier_norm", "tag"])["Net amount"].sum().reset_index()
    tag_gbp = tag_gbp.sort_values(["supplier_norm", "Net amount"], ascending=[True, False])
    dom = tag_gbp.groupby("supplier_norm").first()["tag"].rename("dominant_tag")
    ntag = tag_gbp.groupby("supplier_norm")["tag"].nunique().rename("n_tags")

    def top_val(col):
        return (df.groupby(["supplier_norm", col])["Net amount"].sum().reset_index()
                .sort_values(["supplier_norm", "Net amount"], ascending=[True, False])
                .groupby("supplier_norm").first()[col])

    name = df.groupby("supplier_norm")["Supplier name"].agg(lambda s: s.value_counts().index[0])
    t = tot.join(dom).join(ntag)
    t["spans_tags"] = t["n_tags"] > 1
    t["supplier"] = name
    t["top_narrative"] = top_val("Narrative")
    t["top_service"] = top_val("Service")
    t["annualised estimate"] = t["total_gbp"] * factor
    t["row_ids"] = df.groupby("supplier_norm")["row_id"].agg(lambda s: "; ".join(s))
    return t.reset_index()


def test_high_value(sup, lowest_comp, statutory_value):
    T = lowest_comp["value"]
    hv = sup[reaches(sup["annualised estimate"], lowest_comp)].copy()
    hv = hv.sort_values("annualised estimate", ascending=False)
    hv.drop(columns=["row_ids"]).to_csv(os.path.join(FULL, "high-value-suppliers.csv"), index=False)
    cols = ["supplier", "supplier_norm", "annualised estimate", "total_gbp", "n_payments", "top_narrative",
            "top_service", "dominant_tag", "spans_tags"]
    by_tag = {k: {"suppliers": int(len(v)), "gbp": r2(v["total_gbp"].sum()),
                  "annualised_estimate_gbp": r2(v["annualised estimate"].sum())} for k, v in hv.groupby("dominant_tag")}
    tables = {}
    for k, v in hv.groupby("dominant_tag"):
        if k == "general_procurement":
            continue
        tables[k] = [{**{c: (r2(x) if isinstance(x, float) else x) for c, x in rec.items()}}
                     for rec in v[cols].head(TOP).to_dict("records")]
    gp = hv[hv["dominant_tag"] == "general_procurement"]
    res = {
        "parameters": {"threshold": T, "inclusive": lowest_comp["inclusive"],
                       "basis": "annualised estimate = 3-month total x annualisation factor",
                       "statutory_threshold": statutory_value},
        "rule_ids": lowest_comp["rule_ids"],
        "description": f"suppliers with annualised estimate at or above £{T:,.0f}",
        "suppliers": int(len(hv)), "gbp": r2(hv["total_gbp"].sum()),
        "annualised_estimate_gbp": r2(hv["annualised estimate"].sum()),
        "spanning_several_tags": int(hv["spans_tags"].sum()),
        "by_dominant_tag": by_tag,
        "headline_general_procurement": {
            "suppliers": int(len(gp)), "gbp": r2(gp["total_gbp"].sum()),
            "annualised_estimate_gbp": r2(gp["annualised estimate"].sum()),
            "top20": [{c: (r2(x) if isinstance(x, float) else x) for c, x in rec.items()}
                      for rec in gp[cols].head(TOP).to_dict("records")]},
        "other_tag_tables_top20": tables,
        "note": "population for which contract evidence is requested in fieldwork (Phase 3 PBC list)",
        "full_list": "outputs/analytics-full/high-value-suppliers.csv",
    }
    return res, hv


def test_duplicates(df):
    d = df.copy()
    d["d"] = pd.to_datetime(d["pay_date"])
    d["amt"] = d["Net amount"].round(2)
    d = d.sort_values(["supplier_norm", "amt", "d", "row_id"])
    gap = d.groupby(["supplier_norm", "amt"])["d"].diff().dt.days
    new = gap.isna() | (gap > DUP_WINDOW_DAYS)
    d["grp"] = new.cumsum()
    sizes = d.groupby("grp")["row_id"].transform("count")
    dup = d[sizes >= 2]
    groups = []
    for gid, g in dup.groupby("grp"):
        same_ts = g["Date"].nunique() == 1
        groups.append({
            "supplier": g["Supplier name"].iloc[0], "supplier_norm": g["supplier_norm"].iloc[0],
            "amount": r2(g["amt"].iloc[0]), "n_rows": int(len(g)),
            "first_date": str(g["d"].min().date()), "last_date": str(g["d"].max().date()),
            "tier": "same_timestamp" if same_ts else "different_time",
            "gbp_beyond_first": r2(g["amt"].iloc[0] * (len(g) - 1)),
            "tag": g["tag"].value_counts().index[0], "services": "; ".join(sorted(g["Service"].astype(str).unique())),
            "row_ids": "; ".join(g["row_id"]),
        })
    gd = pd.DataFrame(groups)
    gd.to_csv(os.path.join(FULL, "duplicates.csv"), index=False)
    tiers = {}
    for tier in ["same_timestamp", "different_time"]:
        v = gd[gd["tier"] == tier] if not gd.empty else gd
        if v.empty:
            tiers[tier] = {"groups": 0, "rows": 0, "gbp_beyond_first": 0.0, "by_tag": {}, "top20": []}
            continue
        tiers[tier] = {
            "groups": int(len(v)), "rows": int(v["n_rows"].sum()), "gbp_beyond_first": r2(v["gbp_beyond_first"].sum()),
            "by_tag": {k: {"groups": int(len(x)), "gbp_beyond_first": r2(x["gbp_beyond_first"].sum())}
                       for k, x in v.groupby("tag")},
            "top20": v.sort_values("amount", ascending=False).head(TOP).to_dict("records"),
        }
    return {"parameters": {"window_days": DUP_WINDOW_DAYS, "amount_match": "to the penny",
                           "grouping": "same normalised supplier and amount; payments chained when consecutive "
                                       "calendar dates are within 7 days",
                           "tier_rule": "same_timestamp when every row in the group has an identical Date"},
            "description": "same supplier, same amount, calendar dates within 7 days",
            "lower_bound_note": "payments of £500 or less are not published",
            "tiers": tiers, "full_list": "outputs/analytics-full/duplicates.csv"}


def main():
    rules = load_rules()
    with open(os.path.join(FULL, "cleaning-log.json")) as f:
        clog = json.load(f)
    df = pd.read_csv(os.path.join(FULL, "spend-clean.csv"))
    months = clog["months_covered"]
    factor = 12 / months

    params = rules.get("parameters", {})
    stat = params.get("STATUTORY_THRESHOLD_GOODS_SERVICES", {}).get("value")
    thresholds = build_thresholds(rules)
    comp = [t for t in thresholds if t["competition_triggering"]]
    if not comp:
        print("STOP: no competition-triggering threshold derived from rules.json")
        sys.exit(1)
    lowest_comp = comp[0]
    anti_ids = [r["rule_id"] for r in rules["rules"] if r.get("type") == "anti-avoidance"]
    row_d = rule_ids_for_clause(rules, "App C row D")
    row_e = rule_ids_for_clause(rules, "App C row E")
    row_f = rule_ids_for_clause(rules, "App C row F")
    excluded_clauses = {e.get("clause") for e in rules.get("excluded", [])}

    skipped = []
    if stat is None:
        for test in ["threshold_clustering", "split_purchases", "high_value_suppliers", "off_contract"]:
            skipped.append({"test": test, "tier": "statutory",
                            "reason": "STATUTORY_THRESHOLD_GOODS_SERVICES is null in rules.json"})

    tests = {}
    tests["threshold_clustering"] = test_threshold_clustering(df, thresholds)
    tests["split_purchases"] = test_split_purchases(df, comp, anti_ids)
    sup = supplier_table(df, factor)
    hv_block, hv = test_high_value(sup, lowest_comp, stat)
    tests["high_value_suppliers"] = hv_block
    tests["duplicates"] = test_duplicates(df)

    contracts = clog.get("contracts", {})
    contracts_present = bool(contracts.get("contracts_present"))
    register_present = bool(clog.get("register_present"))
    matching = {}
    if contracts_present or register_present:
        notices = pd.read_csv(os.path.join(FULL, "notices-clean.csv"))
        notices["supplier_norm"] = notices["supplier_norm"].fillna("")
        active = notices[notices["active"]]
        ended = notices[notices["ended_before_window"]]
        spend_sups = sorted(df["supplier_norm"].unique())
        m = match_suppliers(spend_sups, active["supplier_norm"].unique())
        sup_gbp = df.groupby("supplier_norm")["Net amount"].sum()
        m["spend_total_gbp"] = m["supplier_norm"].map(sup_gbp).round(2)
        m["annualised estimate"] = (m["spend_total_gbp"] * factor).round(2)
        m.to_csv(os.path.join(FULL, "supplier-match.csv"), index=False)
        near = m[m["match_class"].isin(["near_ratio", "near_contain"])]
        near.to_csv(os.path.join(FULL, "near-matches.csv"), index=False)
        vc = m["match_class"].value_counts()
        matching = {k: int(vc.get(k, 0)) for k in ["exact", "near_ratio", "near_contain", "none"]}
        matching["against"] = "active notice suppliers (end date on or after spend window start, or blank)"
        matching["near_matches_file"] = "outputs/analytics-full/near-matches.csv"
        matching["note"] = "near matches are candidates for the auditor to confirm, never counted as matches"

        # off_contract
        hvm = hv.merge(m[["supplier_norm", "match_class", "candidate"]], on="supplier_norm", how="left")
        hvm.drop(columns=["row_ids"]).to_csv(os.path.join(FULL, "off-contract.csv"), index=False)
        per_class = {k: {"suppliers": int(len(v)), "gbp": r2(v["total_gbp"].sum()),
                         "annualised_estimate_gbp": r2(v["annualised estimate"].sum())}
                     for k, v in hvm.groupby("match_class")}
        un = hvm[hvm["match_class"] == "none"]
        un_tag = {k: {"suppliers": int(len(v)), "gbp": r2(v["total_gbp"].sum()),
                      "annualised_estimate_gbp": r2(v["annualised estimate"].sum())} for k, v in un.groupby("dominant_tag")}
        ungp = un[un["dominant_tag"] == "general_procurement"].sort_values("annualised estimate", ascending=False)
        cols = ["supplier", "supplier_norm", "annualised estimate", "total_gbp", "n_payments", "top_narrative",
                "top_service", "spans_tags"]
        tests["off_contract"] = {
            "parameters": {"threshold": lowest_comp["value"], "inclusive": lowest_comp["inclusive"],
                           "basis": "annualised estimate", "statutory_tier": "skipped" if stat is None else stat},
            "rule_ids": sorted(set(lowest_comp["rule_ids"]) | set(row_f)),
            "description": "high-value suppliers with no exact-name match to an active Contracts Finder notice",
            "contracts_present": contracts_present, "register_present": register_present,
            "caveat": CAVEAT,
            "scope_note": "Only suppliers at or above the publication threshold are classed; Contracts Finder does "
                          "not carry smaller awards, so results must never be used to question smaller suppliers. "
                          "Exact matching is by name only; the spend data carries no Companies House number.",
            "per_match_class": per_class,
            "unmatched_by_dominant_tag": un_tag,
            "unmatched_general_procurement": {
                "suppliers": int(len(ungp)), "gbp": r2(ungp["total_gbp"].sum()),
                "annualised_estimate_gbp": r2(ungp["annualised estimate"].sum()),
                "top20": [{c: (r2(x) if isinstance(x, float) else x) for c, x in rec.items()}
                          for rec in ungp[cols].head(TOP).to_dict("records")]},
            "placement_note": f"placements are exempt from competition under {row_f} (App C row F)",
            "full_list": "outputs/analytics-full/off-contract.csv",
        }

        # expired_notice_spend
        ended_set = set(ended["supplier_norm"])
        active_set = set(active["supplier_norm"])
        exp_sups = [s for s in spend_sups if s in ended_set and s not in active_set]
        rows = []
        for s in exp_sups:
            e = ended[ended["supplier_norm"] == s].sort_values("Contract end date")
            last = e.iloc[-1]
            srow = sup[sup["supplier_norm"] == s].iloc[0]
            rows.append({"supplier": srow["supplier"], "supplier_norm": s, "total_gbp": r2(srow["total_gbp"]),
                         "annualised estimate": r2(srow["annualised estimate"]), "n_payments": int(srow["n_payments"]),
                         "dominant_tag": srow["dominant_tag"], "latest_end_date": last["Contract end date"],
                         "notice_id": last["Notice Identifier"], "notice_title": last["Title"],
                         "matched_notices": int(e["Notice Identifier"].nunique())})
        ex = pd.DataFrame(rows)
        if not ex.empty:
            ex = ex.sort_values("annualised estimate", ascending=False)
        ex.to_csv(os.path.join(FULL, "expired-notice-spend.csv"), index=False)
        tests["expired_notice_spend"] = {
            "parameters": {"match": "exact normalised name", "window_start": clog["date_min"],
                           "condition": "every matched notice ended before the spend window starts"},
            "rule_ids": row_d,
            "description": "suppliers paid in the window whose every matching notice ended before the window",
            "caveat": "indicator of spend after expiry without an approved extension; a newer contract may exist "
                      "with no notice. " + CAVEAT,
            "suppliers": int(len(ex)),
            "gbp": r2(ex["total_gbp"].sum()) if not ex.empty else 0.0,
            "annualised_estimate_gbp": r2(ex["annualised estimate"].sum()) if not ex.empty else 0.0,
            "top20": ex.head(TOP).to_dict("records") if not ex.empty else [],
            "full_list": "outputs/analytics-full/expired-notice-spend.csv",
        }

        # spend_vs_award
        q = active[(active["suppliers_on_notice"] == 1) & (active["Awarded Value"].fillna(0) > 0)].copy()
        q["start"] = pd.to_datetime(q["Contract start date"])
        q["end"] = pd.to_datetime(q["Contract end date"])
        q["contract_years"] = (q["end"] - q["start"]).dt.days / 365.25
        exact_sups = set(m.loc[m["match_class"] == "exact", "supplier_norm"])
        q = q[q["supplier_norm"].isin(exact_sups)]
        counts = q.groupby("supplier_norm")["Notice Identifier"].nunique()
        multi = sorted(counts[counts > 1].index)
        single = q[q["supplier_norm"].isin(counts[counts == 1].index)]
        bad_dates = single[~(single["contract_years"] > 0)]
        single = single[single["contract_years"] > 0].copy()
        single["award_annual_rate"] = single["Awarded Value"] / single["contract_years"]
        single = single.merge(sup[["supplier_norm", "supplier", "total_gbp", "annualised estimate"]],
                              on="supplier_norm", how="left")
        single["ratio"] = single["annualised estimate"] / single["award_annual_rate"]
        single = single.sort_values("ratio", ascending=False)
        keep_cols = ["supplier", "supplier_norm", "Notice Identifier", "Title", "Awarded Value", "Contract start date",
                     "Contract end date", "contract_years", "award_annual_rate", "total_gbp", "annualised estimate",
                     "ratio"]
        single[keep_cols].to_csv(os.path.join(FULL, "spend-vs-award.csv"), index=False)
        flag = single[single["ratio"] >= SPEND_VS_AWARD_RATIO]
        tests["spend_vs_award"] = {
            "parameters": {"ratio_flag": SPEND_VS_AWARD_RATIO,
                           "award_annual_rate": "Awarded Value / contract years (end - start days / 365.25)",
                           "ratio": "annualised estimate / award_annual_rate",
                           "eligible": "exact match to exactly one active single-supplier notice with Awarded Value > 0"},
            "rule_ids": row_e,
            "description": f"annualised estimate at least {SPEND_VS_AWARD_RATIO} x the award's annual rate",
            "caveat": "award values may be estimates or maxima; indicator of spend beyond the award without an "
                      "approved variation, to confirm against the contract",
            "suppliers_assessed": int(len(single)),
            "excluded_multiple_qualifying_notices": len(multi),
            "excluded_unusable_contract_dates": int(len(bad_dates)),
            "flagged": int(len(flag)),
            "flagged_gbp": r2(flag["total_gbp"].sum()) if not flag.empty else 0.0,
            "flagged_annualised_estimate_gbp": r2(flag["annualised estimate"].sum()) if not flag.empty else 0.0,
            "top20": [{c: (r2(x) if isinstance(x, (float, np.floating)) else x) for c, x in rec.items()}
                      for rec in single[keep_cols].head(TOP).to_dict("records")],
            "full_list": "outputs/analytics-full/spend-vs-award.csv",
        }
    else:
        reason = "no contracts.csv or contract register in data/"
        for test in ["off_contract", "expired_notice_spend", "spend_vs_award"]:
            tests[test] = {"skipped": True, "reason": reason}
            skipped.append({"test": test, "tier": "all", "reason": reason})

    population = {
        "files": list(clog["files"].keys()), "file_detail": clog["files"],
        "rows_raw": clog["rows_raw"], "rows_after_exclusions": clog["rows_after_exclusions"],
        "date_min": clog["date_min"], "date_max": clog["date_max"], "months_covered": months,
        "annualisation_factor": factor, "total_gbp_raw": clog["total_gbp_raw"], "total_gbp": clog["total_gbp"],
        "excluded": clog["excluded"], "tags": clog["tags"], "tag_regexes": clog["regexes"],
        "limitations": ["population is expenditure over £500 only", "Date is a payment-run timestamp",
                        "annualised estimate = 3-month total x annualisation factor; seasonal spend is not adjusted",
                        "Net amount excludes VAT; rules.json notes a VAT ambiguity between clause 6.15 and App B"],
        "rule_refs": {"placements_exempt_App_C_row_F": row_f, "extension_App_C_row_D": row_d,
                      "variation_App_C_row_E": row_e,
                      "grant_as_contract_clause_1_6_2": (rule_ids_for_clause(rules, "1.6.2") or
                                                         ("in rules.json excluded list (definition), no rule_id"
                                                          if "1.6.2" in excluded_clauses else "not found"))},
    }
    contracts_out = {k: contracts.get(k) for k in [
        "rows_in_file", "rows_for_council", "notices", "notice_supplier_pairs", "distinct_suppliers",
        "active_in_window", "ended_before_window", "zero_value_awards", "rows_per_year", "published_range",
        "organisation_names_kept", "rows_dropped_other_buyers"]}
    contracts_out.update({"contracts_present": contracts_present, "register_present": register_present,
                          "warnings": contracts.get("warnings", []), "caveat": CAVEAT})
    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "scripts": ["scripts/clean.py", "scripts/analyse.py", "scripts/selfcheck.py"],
        "population": population,
        "thresholds": [{k: t[k] for k in ["value", "inclusive", "inclusive_source", "inclusivity_conflict",
                                         "competition_triggering", "quote_or_tender_mentioned",
                                         "competition_rule_ids", "rule_ids"]} for t in thresholds],
        "competition_triggering_definition": "required_action mentions a tender, invitations to quote, or at least "
                                             "three/five sources; a single quote is not treated as competition",
        "skipped": skipped,
        "contracts": contracts_out,
        "matching": matching,
        "tests": tests,
    }
    with open(os.path.join(ROOT, "outputs", "analytics.json"), "w") as f:
        json.dump(out, f, indent=2, default=str)

    # terminal: headlines only
    print("thresholds", [(t["value"], t["inclusive"], t["competition_triggering"]) for t in thresholds])
    for b in tests["threshold_clustering"]["per_threshold"]:
        print("cluster", b["threshold"], b["band_count"], b["band_gbp"], "| comp", b["comparator_count"],
              b["comparator_gbp"], "| base", b["baseline_count"])
    for b in tests["split_purchases"]["per_threshold"]:
        print("split", b["threshold"], b["windows"], b["suppliers"], b["gbp"],
              {k: v["windows"] for k, v in b.get("by_tag", {}).items()},
              "gp", b.get("headline_general_procurement", {}).get("windows"),
              b.get("headline_general_procurement", {}).get("gbp"))
    h = tests["high_value_suppliers"]
    print("highvalue", h["suppliers"], h["gbp"], h["annualised_estimate_gbp"], "gp",
          h["headline_general_procurement"]["suppliers"], h["headline_general_procurement"]["gbp"],
          {k: v["suppliers"] for k, v in h["by_dominant_tag"].items()})
    for k, v in tests["duplicates"]["tiers"].items():
        print("dup", k, v["groups"], v["rows"], v["gbp_beyond_first"])
    print("matching", matching)
    if "per_match_class" in tests.get("off_contract", {}):
        oc = tests["off_contract"]
        print("offcontract", oc["per_match_class"], "ungp", oc["unmatched_general_procurement"]["suppliers"],
              oc["unmatched_general_procurement"]["gbp"])
        e = tests["expired_notice_spend"]
        print("expired", e["suppliers"], e["gbp"], e["annualised_estimate_gbp"])
        s = tests["spend_vs_award"]
        print("spend_vs_award", s["suppliers_assessed"], s["flagged"], s["flagged_gbp"],
              s["excluded_multiple_qualifying_notices"], s["excluded_unusable_contract_dates"])


if __name__ == "__main__":
    main()
