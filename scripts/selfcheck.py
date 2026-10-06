"""Re-derive one flagged item per test from spend-clean.csv, independently of analyse.py.

Prints only the checks. Exit code 1 if any check fails.
"""
import json
import os
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FULL = os.path.join(ROOT, "outputs", "analytics-full")
A = json.load(open(os.path.join(ROOT, "outputs", "analytics.json")))
df = pd.read_csv(os.path.join(FULL, "spend-clean.csv"))
df["d"] = pd.to_datetime(df["pay_date"])
factor = A["population"]["annualisation_factor"]
fails = 0


def check(name, expected, got, ids):
    global fails
    ok = abs(float(expected) - float(got)) < 0.01
    fails += 0 if ok else 1
    print(f"{'PASS' if ok else 'FAIL'} {name}: reported {expected} re-derived {round(float(got), 2)} row_ids {ids}")


# 1 threshold clustering: top row of the competition threshold band, re-check amount and band membership
tc = [b for b in A["tests"]["threshold_clustering"]["per_threshold"] if b["band_count"] > 0]
b = [x for x in tc if x["threshold"] == min(t["value"] for t in A["thresholds"] if t["competition_triggering"])][0]
r = b["top20"][0]
row = df[df["row_id"] == r["row_id"]].iloc[0]
T = b["threshold"]
inband = 0.9 * T <= row["Net amount"] < T
check(f"threshold_clustering T={T} in band={inband}", r["amount"], row["Net amount"], [r["row_id"]])

# 2 split purchases: top general-procurement window, re-sum supplier rows in window dates
sp = A["tests"]["split_purchases"]["per_threshold"][0]
w = sp["headline_general_procurement"]["top20"][0]
sub = df[(df["Supplier name"] == w["supplier"]) & (df["d"] >= w["window_start"]) & (df["d"] <= w["window_end"])
         & (df["Net amount"] < sp["threshold"])]
check(f"split_purchases T={sp['threshold']} {w['supplier']} n={len(sub)}", w["total_gbp"], sub["Net amount"].sum(),
      w["row_ids"].split("; ")[:3])

# 3 high value suppliers: top general-procurement supplier, re-sum all rows by original name
h = A["tests"]["high_value_suppliers"]["headline_general_procurement"]["top20"][0]
sub = df[df["supplier_norm"] == h["supplier_norm"]]
check(f"high_value_suppliers {h['supplier']} total", h["total_gbp"], sub["Net amount"].sum(),
      sub["row_id"].head(3).tolist())
check(f"high_value_suppliers {h['supplier']} annualised", h["annualised estimate"], sub["Net amount"].sum() * factor, [])

# 4 duplicates: top different_time group, recount rows with that supplier and amount within its dates
g = A["tests"]["duplicates"]["tiers"]["different_time"]["top20"][0]
sub = df[(df["supplier_norm"] == g["supplier_norm"]) & (df["Net amount"].round(2) == g["amount"])
         & (df["d"] >= g["first_date"]) & (df["d"] <= g["last_date"])]
check(f"duplicates {g['supplier']} £{g['amount']} n={len(sub)}", g["gbp_beyond_first"],
      g["amount"] * (len(sub) - 1), g["row_ids"].split("; ")[:3])

# 5 off_contract: top unmatched general-procurement supplier, re-sum and confirm absent from notices
oc = A["tests"].get("off_contract", {})
if "unmatched_general_procurement" in oc and oc["unmatched_general_procurement"]["top20"]:
    u = oc["unmatched_general_procurement"]["top20"][0]
    sub = df[df["supplier_norm"] == u["supplier_norm"]]
    notices = pd.read_csv(os.path.join(FULL, "notices-clean.csv"))
    in_active = bool(((notices["supplier_norm"] == u["supplier_norm"]) & notices["active"]).any())
    check(f"off_contract {u['supplier']} in_active_notices={in_active}", u["total_gbp"], sub["Net amount"].sum(),
          sub["row_id"].head(3).tolist())

# 6 expired_notice_spend: top supplier
ex = A["tests"].get("expired_notice_spend", {})
if ex.get("top20"):
    e = ex["top20"][0]
    sub = df[df["supplier_norm"] == e["supplier_norm"]]
    check(f"expired_notice_spend {e['supplier']} notice {e['notice_id']} ended {e['latest_end_date']}",
          e["total_gbp"], sub["Net amount"].sum(), sub["row_id"].head(3).tolist())

# 7 spend_vs_award: top ratio supplier
sv = A["tests"].get("spend_vs_award", {})
if sv.get("top20"):
    s = sv["top20"][0]
    sub = df[df["supplier_norm"] == s["supplier_norm"]]
    check(f"spend_vs_award {s['supplier']} notice {s['Notice Identifier']} ratio {s['ratio']}",
          s["annualised estimate"], sub["Net amount"].sum() * factor, sub["row_id"].head(3).tolist())

print("selfcheck failures:", fails)
sys.exit(1 if fails else 0)
