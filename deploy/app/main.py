"""Web app for the procurement audit planning harness.

Anyone can watch runs and read their outputs. Starting a run, recording the
auditor's decisions and signing off need the shared passcode, and new runs
are capped per day because each one spends real API credit.
"""
import asyncio, datetime, hmac, json, os, re
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse, StreamingResponse

from . import harness as H

PASSCODE = os.environ.get("RUN_PASSCODE", "")
DAILY_CAP = int(os.environ.get("RUNS_PER_DAY", "3"))
STATIC = Path(__file__).parent / "static"
REFERENCE = Path(os.environ.get("REFERENCE_DIR", "/app/reference"))
OUTPUT_FILES = ["rules.json", "analytics.json", "history.json", "risk-register.md", "auditor-comments.md",
                "risk-ratings.json", "planning-memo.md", "risk-control-matrix.md", "audit-program.md",
                "challenges.md", "review.md", "audit-plan.json", "pack-figures.json"]

app = FastAPI(title="Procurement audit planner harness")
H.RUNS.mkdir(parents=True, exist_ok=True)
tasks: dict[str, asyncio.Task] = {}


@app.on_event("startup")
def mark_interrupted():
    """A run that was working when the server stopped cannot resume its sessions."""
    for p in H.RUNS.iterdir():
        sp = p / "state.json"
        if sp.exists():
            st = json.loads(sp.read_text())
            if st.get("status") == "running":
                run = H.Run(p.name)
                for s in st["stages"].values():
                    if s.get("status") == "running":
                        s["status"] = "failed"
                st.update(status="failed", error="Interrupted: the server restarted while this run was working.")
                run.save(st)
                run.event(kind="error", text="Interrupted by a server restart.")


def check_pass(body: dict):
    if not PASSCODE:
        raise HTTPException(503, "Runs are disabled: no passcode is configured on the server.")
    if not hmac.compare_digest(str(body.get("passcode", "")), PASSCODE):
        raise HTTPException(403, "Wrong passcode.")


def busy() -> str | None:
    for rid, t in tasks.items():
        if not t.done():
            return rid
    return None


def get_run(rid: str) -> H.Run:
    if not re.fullmatch(r"[\w-]+", rid):
        raise HTTPException(404)
    if rid == "reference":
        raise HTTPException(400, "The reference run is read-only.")
    run = H.Run(rid)
    if not run.state_path.exists():
        raise HTTPException(404, "No such run.")
    return run


def run_dirs():
    return sorted([p for p in H.RUNS.iterdir() if (p / "state.json").exists()], reverse=True)


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/config")
def config():
    today = datetime.datetime.utcnow().strftime("%Y%m%d")
    used = sum(1 for p in run_dirs() if p.name.startswith(today))
    return {"model": H.MODEL, "stages": [{k: s[k] for k in ("id", "title", "kind", "who") if k in s} | {"human": s.get("human", False)}
                                         for s in H.STAGES],
            "runs_today": used, "daily_cap": DAILY_CAP, "busy": busy(), "runs_enabled": bool(PASSCODE),
            "stage_budget_usd": H.STAGE_BUDGET}


@app.get("/api/runs")
def runs():
    out = []
    if (REFERENCE / "state.json").exists():
        out.append(json.loads((REFERENCE / "state.json").read_text()) | {"id": "reference"})
    for p in run_dirs():
        st = json.loads((p / "state.json").read_text())
        out.append({k: st.get(k) for k in ("id", "label", "created", "status", "current", "cost_usd")})
    return out


def run_root(rid: str) -> Path:
    if rid == "reference":
        return REFERENCE
    if not re.fullmatch(r"[\w-]+", rid) or not (H.RUNS / rid / "state.json").exists():
        raise HTTPException(404, "No such run.")
    return H.RUNS / rid


def outputs_dir(rid: str) -> Path:
    root = run_root(rid)
    return root / "outputs" if rid == "reference" else root / "workspace" / "outputs"


@app.get("/api/runs/{rid}")
def run_state(rid: str):
    root = run_root(rid)
    st = json.loads((root / "state.json").read_text())
    out = outputs_dir(rid)
    st["files"] = [f for f in OUTPUT_FILES if (out / f).exists()]
    st["samples"] = sorted(p.name for p in (out / "samples").glob("T-*.csv")) if (out / "samples").exists() else []
    st["register"] = H.register_rows(out.parent)
    return st


@app.get("/api/runs/{rid}/files/{name:path}")
def run_file(rid: str, name: str):
    out = outputs_dir(rid)
    p = (out / name).resolve()
    if not str(p).startswith(str(out.resolve())) or not p.is_file():
        raise HTTPException(404)
    return PlainTextResponse(p.read_text(encoding="utf-8", errors="replace"))


@app.get("/api/runs/{rid}/events")
async def run_events(rid: str, request: Request, since: int = 0):
    path = run_root(rid) / "events.jsonl"

    async def gen():
        pos = since
        while True:
            if await request.is_disconnected():
                return
            lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
            for i in range(pos, len(lines)):
                yield f"id: {i + 1}\ndata: {lines[i]}\n\n"
            pos = len(lines)
            if rid == "reference" or not (rid in tasks and not tasks[rid].done()):
                st = json.loads((run_root(rid) / "state.json").read_text())
                if st.get("status") != "running":
                    yield "event: idle\ndata: {}\n\n"
                    return
            await asyncio.sleep(1.0)

    return StreamingResponse(gen(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"})


@app.post("/api/runs")
async def start_run(request: Request):
    body = await request.json()
    check_pass(body)
    if busy():
        raise HTTPException(409, f"Run {busy()} is still working. One run at a time.")
    today = datetime.datetime.utcnow().strftime("%Y%m%d")
    if sum(1 for p in run_dirs() if p.name.startswith(today)) >= DAILY_CAP:
        raise HTTPException(429, f"Today's limit of {DAILY_CAP} runs is used up. Watch the latest run or the reference run.")
    run = H.Run.create(label=str(body.get("label", ""))[:80])
    tasks[run.id] = asyncio.create_task(H.first_half(run))
    return {"id": run.id}


@app.post("/api/runs/{rid}/gate")
async def gate(rid: str, request: Request):
    body = await request.json()
    check_pass(body)
    run = get_run(rid)
    st = run.state()
    if st["status"] != "awaiting_gate":
        raise HTTPException(409, "This run is not waiting for decisions.")
    if busy():
        raise HTTPException(409, "Another run is working; try again when it finishes.")
    rows = {r["id"] for r in H.register_rows(run.ws)}
    dec = body.get("decisions") or {}
    if set(dec) != rows:
        raise HTTPException(400, f"Record a decision for every risk: {', '.join(sorted(rows - set(dec)))}")
    for k, v in dec.items():
        if v.get("decision") not in ("approve", "amend", "reject"):
            raise HTTPException(400, f"{k}: decision must be approve, amend or reject")
        if v["decision"] in ("amend", "reject") and not str(v.get("comment", "")).strip():
            raise HTTPException(400, f"{k}: say what to change or why it is rejected")
    if not str(body.get("reviewer", "")).strip():
        raise HTTPException(400, "Enter the reviewer's name.")
    H.write_decisions(run, body["reviewer"], dec)
    tasks[run.id] = asyncio.create_task(H.second_half(run))
    return {"ok": True}


@app.post("/api/runs/{rid}/signoff")
async def signoff(rid: str, request: Request):
    body = await request.json()
    check_pass(body)
    run = get_run(rid)
    if run.state()["status"] != "awaiting_signoff":
        raise HTTPException(409, "This run is not waiting for sign-off.")
    decision = body.get("decision")
    if decision not in ("sign off", "return to the team"):
        raise HTTPException(400, "Decision must be 'sign off' or 'return to the team'.")
    review = (run.ws / "outputs" / "review.md").read_text(encoding="utf-8")
    if decision == "sign off" and "READY FOR SIGN-OFF" not in review:
        raise HTTPException(409, "The QA verdict is not READY FOR SIGN-OFF, so the pack cannot be signed off.")
    if not str(body.get("name", "")).strip():
        raise HTTPException(400, "Enter your name.")
    H.write_signoff(run, body["name"], decision, body.get("comment", ""))
    return {"ok": True}


@app.get("/healthz")
def healthz():
    return JSONResponse({"ok": True})
