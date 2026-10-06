#!/usr/bin/env python3
"""Package the Part A run as the read-only reference run shown by the web app.

Usage: python deploy/make_reference.py   (from the repo root)
Writes deploy/reference/{state.json, events.jsonl, outputs/}.
"""
import json, re, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "deploy" / "reference"
KEEP = ["rules.json", "analytics.json", "history.json", "risk-ratings.json", "risk-register.md",
        "auditor-comments.md", "audit-plan.json", "planning-memo.md", "risk-control-matrix.md",
        "audit-program.md", "pack-figures.json", "challenges.md", "review.md"]

STAGES = {
    "rules": ("2.1 to 2.2", "extract-rules skill run on the Contract Rules PDF. 65 testable rules, 99 excluded clauses, "
              "4 statutory thresholds left null. verify_quotes.py: ALL CHECKS PASSED (65 rules, 99 excluded, 0 warning(s))."),
    "analysis": ("3.1 to 3.4", "spend-analyst: 10,607 payments read, 8,534 kept, 7 indicator tests, self-check 8 of 8. "
                 "findings-analyst: 20 audits, 10 risk themes, the council's 5x5 scoring method; 130 quotes verified; "
                 "three items checked against rendered PDF pages, all matched."),
    "register": ("3.5 to 3.7", "risk-assessment skill written from the guide's prompt and tested on fixtures. risk-assessor rated "
                 "10 risks; build_register.py: warnings 0, failures 0; no supplier names in risk text."),
    "gate": ("4.1 to 4.2", "Jeremy Lee, 2026-10-06: approve R-02 to R-09, amend R-01 (bring into scope), reject R-10 (covered by R-04)."),
    "revision": ("4.3 and 5.1", "Register revision 1: R-01 amended, R-10 rejected. build_pack.py --gate: gate closed, 9 risks in scope."),
    "team": ("5.2 to 5.7", "planner, challenger and qa-reviewer: 3 pack versions, 12 challenges in 2 rounds (11 resolved, 1 for the "
             "auditor), QA v3 READY FOR SIGN-OFF (4/4 checks). 9 risks, 11 controls, 17 tests, 229 sampled payments."),
    "signoff": ("5.8", "Signed off by Jeremy Lee on 2026-10-06, noting challenge #2 (R-03 likelihood)."),
}


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "outputs" / "samples").mkdir(parents=True)
    src = ROOT / "outputs"
    for f in KEEP:
        shutil.copy2(src / f, OUT / "outputs" / f)
    for f in (src / "samples").glob("T-*.csv"):
        shutil.copy2(f, OUT / "outputs" / "samples" / f.name)

    ev = [{"kind": "run", "t": "2026-10-06T07:00:00+00:00",
           "text": "Reference run: the Part A build, done step by step from the guide in Claude Code. "
                   "This log summarises each stage; the full documents are under Documents."}]
    for sid, (steps, text) in STAGES.items():
        ev.append({"kind": "stage", "stage": sid, "text": f"Guide steps {steps}"})
        ev.append({"kind": "gate" if sid in ("gate", "signoff") else "text", "stage": sid, "who": "summary", "text": text})
        if sid == "team":
            for line in (ROOT / "docs" / "team-messages.md").read_text(encoding="utf-8").splitlines():
                m = re.match(r"^\| (\d+) \| ([\w-]+) \| ([\w-]+) \| (.*) \|$", line)
                if m:
                    ev.append({"kind": "tool", "stage": "team", "who": m.group(2),
                               "text": f"message to {m.group(3)}: {m.group(4)}"})
    with (OUT / "events.jsonl").open("w") as f:
        for e in ev:
            f.write(json.dumps(e) + "\n")

    state = {"id": "reference", "label": "Reference run (Part A build)", "created": "2026-10-06T07:00:00+00:00",
             "status": "signed_off", "current": "signoff", "model": "claude-opus-5-5 (Claude Code session)",
             "cost_usd": None, "stages": {sid: {"status": "done"} for sid in STAGES}}
    (OUT / "state.json").write_text(json.dumps(state, indent=1))
    print(f"wrote {OUT} ({len(ev)} events)")


if __name__ == "__main__":
    main()
