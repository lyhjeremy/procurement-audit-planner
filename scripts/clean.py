"""Clean spend workbooks and the Contracts Finder export for the spend-analyst.

Writes to outputs/analytics-full/:
  spend-clean.csv, spend-excluded.csv, notices-clean.csv, cleaning-log.json

Data under data/ is read-only. Thresholds are not used here.
"""
import glob
import json
import os
import re
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs", "analytics-full")
os.makedirs(OUT, exist_ok=True)

EXPECTED = ["Service", "Expenditure category", "Narrative", "Date", "Net amount", "Supplier name"]
SHEET = "Data to publish"

DROP_TOKENS = {"LTD", "LIMITED", "PLC", "LLP", "LLC", "INC", "CIC", "CIO", "UK", "THE"}

RE_PENSION = r"LGPS|PENSION|SUPERANNUATION"
RE_INTER_SUPPLIER = (r"\b(?:COUNCIL|BOROUGH|COUNTY|CNCL|NHS|POLICE|FIRE AUTHORITY|FIRE AND RESCUE|HMRC|"
                     r"HM REVENUE|DEPARTMENT FOR|MINISTRY OF)\b")
RE_INTER_NARR = r"JOINT ARRANGEMENTS"
NARR_PRIVATE = "PRIVATE CONTRACTORS"

PLACEMENT_SERVICES = ("Adult Social Care", "Children's Social Care", "Education")
PLACEMENT_NARRATIVES = {"Private Contractors", "Other agencies", "Voluntary Associations"}
RE_GRANT = r"GRANT"
RE_AGENCY = r"AGENCY"
RE_PREMISES = r"RENT|RATES|WATER RATES|LEASE"

COUNCIL_NAMES = {"west berkshire council", "west berkshire"}


def stop(msg):
    print("STOP:", msg)
    sys.exit(1)


def normalise_supplier(name):
    if name is None or (isinstance(name, float) and pd.isna(name)):
        return ""
    s = str(name).upper()
    s = s.replace("&", " AND ")
    s = re.sub(r"\([^)]*\)", " ", s)
    s = re.sub(r"\[[^\]]*\]", " ", s)
    s = re.sub(r"\bT/A\b.*$", " ", s)
    s = re.sub(r"\bTRADING AS\b.*$", " ", s)
    s = re.sub(r"[^A-Z0-9 ]", " ", s)
    toks = [t for t in s.split() if t not in DROP_TOKENS]
    return " ".join(toks)


def load_spend():
    files = sorted(glob.glob(os.path.join(ROOT, "data", "spend", "*.xlsx")) +
                   glob.glob(os.path.join(ROOT, "data", "spend", "*.csv")))
    if not files:
        stop("no spend files in data/spend/")
    frames, per_file = [], {}
    for p in files:
        fname = os.path.basename(p)
        if p.endswith(".csv"):
            raw = pd.read_csv(p, header=None)
        else:
            raw = pd.read_excel(p, sheet_name=SHEET, header=None)
        hdr = [i for i in range(len(raw)) if str(raw.iloc[i, 0]).strip() == "Service"]
        if not hdr:
            stop(f"{fname}: no header row starting with 'Service'")
        h = hdr[0]
        if p.endswith(".csv"):
            df = pd.read_csv(p, header=h)
        else:
            df = pd.read_excel(p, sheet_name=SHEET, header=h)
        df.columns = [str(c).strip() for c in df.columns]
        if list(df.columns) != EXPECTED:
            stop(f"{fname}: columns {list(df.columns)} != {EXPECTED}")
        # sheet row: header is 0-based row h -> Excel row h+1; first data row is h+2
        df["sheet_row"] = df.index + h + 2
        df["source_file"] = fname
        df["row_id"] = fname + ":" + df["sheet_row"].astype(str)
        if not pd.api.types.is_datetime64_any_dtype(df["Date"]):
            df["Date"] = pd.to_datetime(df["Date"], dayfirst=False, errors="coerce")
        df["Net amount"] = pd.to_numeric(df["Net amount"], errors="coerce")
        for col in ["Date", "Net amount", "Supplier name"]:
            n = int(df[col].isna().sum())
            if n:
                stop(f"{fname}: {n} null or unparseable values in {col}")
        neg = int((df["Net amount"] < 0).sum())
        if neg:
            stop(f"{fname}: {neg} negative amounts")
        per_file[fname] = {"header_row_excel": h + 1, "rows": int(len(df))}
        frames.append(df)
    spend = pd.concat(frames, ignore_index=True)
    spend["pay_date"] = spend["Date"].dt.normalize().dt.date
    spend["supplier_norm"] = spend["Supplier name"].map(normalise_supplier)
    return spend, per_file


def exclusions(spend):
    sup_u = spend["Supplier name"].astype(str).str.upper()
    narr_u = spend["Narrative"].astype(str).str.upper()
    redacted = spend["Supplier name"].astype(str).str.strip().str.lower() == "redacted"
    pension = narr_u.str.contains(RE_PENSION, regex=True)
    inter = ((sup_u.str.contains(RE_INTER_SUPPLIER, regex=True) | narr_u.str.contains(RE_INTER_NARR, regex=True))
             & (narr_u.str.strip() != NARR_PRIVATE))
    reason = pd.Series("", index=spend.index)
    reason[inter] = "inter_authority"
    reason[pension] = "pension_statutory"
    reason[redacted] = "redacted_supplier"  # first match wins: redacted, pension, inter-authority
    spend["exclusion"] = reason
    return spend


def tag(spend):
    narr = spend["Narrative"].astype(str)
    narr_u = narr.str.upper()
    svc = spend["Service"].astype(str)
    placement = svc.str.startswith(PLACEMENT_SERVICES) & narr.str.strip().isin(PLACEMENT_NARRATIVES)
    t = pd.Series("general_procurement", index=spend.index)
    t[narr_u.str.contains(RE_PREMISES, regex=True)] = "premises_non_procurement"
    t[narr_u.str.contains(RE_AGENCY, regex=True)] = "agency_staff"
    t[narr_u.str.contains(RE_GRANT, regex=True)] = "grant"
    t[placement] = "care_or_education_placement"  # assigned last so the first rule in order wins
    spend["tag"] = t
    return spend


def split_suppliers(field):
    if not isinstance(field, str) or not field.strip():
        return []
    s = field.strip()
    if s.startswith("["):
        s = s[1:]
    if s.endswith("]"):
        s = s[:-1]
    out = []
    for block in s.split("]["):
        parts = block.split("|")
        name = parts[0].strip() if parts else ""
        ch = ""
        if len(parts) >= 4 and parts[2].strip().upper() == "COMPANIES_HOUSE":
            ch = parts[3].strip()
        if name:
            out.append((name, ch))
    return out


def load_contracts(window_start):
    path = os.path.join(ROOT, "data", "contracts.csv")
    log = {"contracts_present": os.path.exists(path)}
    if not log["contracts_present"]:
        return None, log
    c = pd.read_csv(path)
    log["rows_in_file"] = int(len(c))
    keep = c["Organisation Name"].astype(str).str.strip().str.lower().isin(COUNCIL_NAMES)
    log["organisation_names_kept"] = {k: int(v) for k, v in c.loc[keep, "Organisation Name"].value_counts().items()}
    log["organisation_names_dropped"] = {k: int(v) for k, v in c.loc[~keep, "Organisation Name"].value_counts().items()}
    log["rows_dropped_other_buyers"] = int((~keep).sum())
    c = c[keep].copy()
    log["rows_for_council"] = int(len(c))
    warnings = []
    if len(c) < 20:
        warnings.append("fewer than 20 notices for the council after filtering; contracts.csv treated as absent")
        log["warnings"] = warnings
        log["contracts_present"] = False
        return None, log
    sup_col = [col for col in c.columns if col.startswith("Supplier [")]
    if len(sup_col) != 1:
        stop(f"contracts.csv: expected one packed Supplier column, found {sup_col}")
    sup_col = sup_col[0]
    for col in ["Contract start date", "Contract end date", "Awarded Date"]:
        c[col] = pd.to_datetime(c[col], format="%d/%m/%Y", errors="coerce")
    c["Published Date"] = pd.to_datetime(c["Published Date"], format="ISO8601", utc=True, errors="coerce")
    c["OJEU Procedure Type"] = c["OJEU Procedure Type"].astype(str).str.strip()
    c["Awarded Value"] = pd.to_numeric(c["Awarded Value"], errors="coerce")
    c["suppliers_on_notice"] = c[sup_col].map(lambda f: len(split_suppliers(f)))
    rows = []
    for _, r in c.iterrows():
        for name, ch in split_suppliers(r[sup_col]):
            rows.append({
                "Notice Identifier": r["Notice Identifier"], "Title": r["Title"],
                "OJEU Procedure Type": r["OJEU Procedure Type"], "Awarded Value": r["Awarded Value"],
                "Contract start date": r["Contract start date"], "Contract end date": r["Contract end date"],
                "Awarded Date": r["Awarded Date"], "Published Date": r["Published Date"],
                "suppliers_on_notice": r["suppliers_on_notice"],
                "supplier_name": name, "companies_house_no": ch, "supplier_norm": normalise_supplier(name),
            })
    n = pd.DataFrame(rows)
    ws = pd.Timestamp(window_start)
    n["active"] = n["Contract end date"].isna() | (n["Contract end date"] >= ws)
    n["ended_before_window"] = ~n["active"]
    notice_active = c["Contract end date"].isna() | (c["Contract end date"] >= ws)
    log.update({
        "notices": int(c["Notice Identifier"].nunique()),
        "notices_without_supplier": int((c["suppliers_on_notice"] == 0).sum()),
        "notice_supplier_pairs": int(len(n)),
        "distinct_suppliers": int(n["supplier_norm"].nunique()),
        "active_in_window": int(notice_active.sum()),
        "ended_before_window": int((~notice_active).sum()),
        "active_pairs": int(n["active"].sum()),
        "ended_pairs": int(n["ended_before_window"].sum()),
        "zero_value_awards": int((c["Awarded Value"].fillna(0) == 0).sum()),
        "rows_per_year": {str(k): int(v) for k, v in c["Published Date"].dt.year.value_counts().sort_index().items()},
        "published_range": [str(c["Published Date"].min().date()), str(c["Published Date"].max().date())],
        "unparsed_end_dates": int(c["Contract end date"].isna().sum()),
    })
    if log["rows_in_file"] == 1000:
        warnings.append("contracts.csv has exactly 1,000 rows: the export may have hit the download cap")
    rpy = log["rows_per_year"]
    if rpy:
        med = pd.Series(list(rpy.values())).median()
        thin = [y for y, v in rpy.items() if v < 0.25 * med]
        if thin:
            warnings.append(f"publication years with under a quarter of the median yearly count: {thin} "
                            "(partial year or export gap)")
    log["warnings"] = warnings
    return n, log


def main():
    spend, per_file = load_spend()
    rows_raw = int(len(spend))
    spend = exclusions(spend)
    spend = tag(spend)
    months = int(pd.to_datetime(spend["pay_date"]).dt.to_period("M").nunique())
    window_start = min(spend["pay_date"])
    window_end = max(spend["pay_date"])

    cols_front = ["row_id", "source_file", "sheet_row", "pay_date", "supplier_norm", "tag"]
    order = cols_front + EXPECTED
    excl = spend[spend["exclusion"] != ""]
    clean = spend[spend["exclusion"] == ""]
    excl[order + ["exclusion"]].to_csv(os.path.join(OUT, "spend-excluded.csv"), index=False)
    clean[order].to_csv(os.path.join(OUT, "spend-clean.csv"), index=False)

    excluded = {}
    reasons = {
        "redacted_supplier": "supplier is 'Redacted' (many payees under one label); unusable for supplier-level tests",
        "pension_statutory": f"narrative matches {RE_PENSION}: statutory pension contributions, not procurement",
        "inter_authority": "payee is a public body (supplier regex) or narrative is joint arrangements, "
                           "narrative not 'Private Contractors'",
    }
    for k, why in reasons.items():
        sub = spend[spend["exclusion"] == k]
        excluded[k] = {"rows": int(len(sub)), "gbp": round(float(sub["Net amount"].sum()), 2), "reason": why}

    tags = {}
    for t, sub in clean.groupby("tag"):
        tags[t] = {"rows": int(len(sub)), "gbp": round(float(sub["Net amount"].sum()), 2),
                   "suppliers": int(sub["supplier_norm"].nunique())}

    notices, clog = load_contracts(window_start)
    if notices is not None:
        out = notices.copy()
        for col in ["Contract start date", "Contract end date", "Awarded Date"]:
            out[col] = out[col].dt.strftime("%Y-%m-%d")
        out["Published Date"] = out["Published Date"].dt.strftime("%Y-%m-%d")
        out.to_csv(os.path.join(OUT, "notices-clean.csv"), index=False)
    reg_present = os.path.exists(os.path.join(ROOT, "data", "contract-register.csv"))

    log = {
        "files": per_file,
        "rows_raw": rows_raw,
        "rows_after_exclusions": int(len(clean)),
        "date_min": str(window_start), "date_max": str(window_end),
        "months_covered": months,
        "total_gbp_raw": round(float(spend["Net amount"].sum()), 2),
        "total_gbp": round(float(clean["Net amount"].sum()), 2),
        "excluded": excluded,
        "tags": tags,
        "regexes": {
            "pension_statutory": RE_PENSION, "inter_authority_supplier": RE_INTER_SUPPLIER,
            "inter_authority_narrative": RE_INTER_NARR, "inter_authority_unless_narrative": NARR_PRIVATE,
            "placement_services_prefix": list(PLACEMENT_SERVICES), "placement_narratives": sorted(PLACEMENT_NARRATIVES),
            "grant": RE_GRANT, "agency_staff": RE_AGENCY, "premises_non_procurement": RE_PREMISES,
            "tag_order": ["care_or_education_placement", "grant", "agency_staff", "premises_non_procurement",
                          "general_procurement"],
        },
        "contracts": clog,
        "register_present": reg_present,
    }
    with open(os.path.join(OUT, "cleaning-log.json"), "w") as f:
        json.dump(log, f, indent=2, default=str)
    print("rows_raw", rows_raw, "clean", len(clean), "excluded", len(excl), "months", months)
    print("excluded", {k: (v["rows"], v["gbp"]) for k, v in excluded.items()})
    print("tags", {k: v["rows"] for k, v in tags.items()})
    print("contracts", {k: clog.get(k) for k in ["rows_in_file", "rows_for_council", "notices", "notice_supplier_pairs",
                                                  "distinct_suppliers", "active_in_window", "ended_before_window",
                                                  "zero_value_awards", "warnings"]})


if __name__ == "__main__":
    main()
