"""Agent harness: runs the Part A system (CLAUDE.md, .claude/skills, .claude/agents)
stage by stage through the Claude Agent SDK, in a fresh workspace per run.

The harness owns orchestration and the two human gates. The model work happens
inside Claude Code sessions that load the project's own files, so the skills
and agents are the same files a person would use in VS Code.
"""
import asyncio, datetime, json, os, re, shutil, time, uuid
from pathlib import Path

from claude_agent_sdk import (AgentDefinition, AssistantMessage, ClaudeAgentOptions, ResultMessage, TextBlock,
                              ToolResultBlock, ToolUseBlock, UserMessage, query)

TEMPLATE = Path(os.environ.get("TEMPLATE_DIR", "/app/template"))
RUNS = Path(os.environ.get("RUNS_DIR", "/data/runs"))
MODEL = os.environ.get("AGENT_MODEL", "claude-sonnet-5-5")
STAGE_BUDGET = float(os.environ.get("STAGE_BUDGET_USD", "6"))

# Stage prompts are the guide's own prompts, with the parallel analysts joined into one stage.
STAGES = [
    {"id": "rules", "title": "Extract the rules", "kind": "Skill", "who": "extract-rules",
     "prompt": "/extract-rules",
     "produces": ["outputs/rules.json"]},
    {"id": "analysis", "title": "Analyse spend and audit history", "kind": "Sub-agents",
     "who": "spend-analyst, findings-analyst",
     "prompt": ("Run the spend-analyst and the findings-analyst sub-agents described in CLAUDE.md. "
                "They are independent, so launch both at once with the Agent tool "
                "(subagent_type spend-analyst and findings-analyst) and wait for both. "
                "Then relay each agent's report in a few lines."),
     "produces": ["outputs/analytics.json", "outputs/history.json"]},
    {"id": "register", "title": "Rate the risks", "kind": "Sub-agent", "who": "risk-assessor",
     "prompt": ("Run the risk-assessor sub-agent (Agent tool, subagent_type risk-assessor). "
                "Then rerun the builder yourself with `.venv/bin/python .claude/skills/risk-assessment/build_register.py`, "
                "show the register's summary table, and check that no supplier name appears in any risk statement or justification."),
     "produces": ["outputs/risk-register.md", "outputs/auditor-comments.md"]},
    {"id": "gate", "title": "Auditor decisions", "kind": "Human gate", "who": "you",
     "human": True, "produces": ["outputs/auditor-comments.md"]},
    {"id": "revision", "title": "Revise the register", "kind": "Sub-agent", "who": "risk-assessor",
     "prompt": ("Run the risk-assessor again (Agent tool, subagent_type risk-assessor). "
                "Apply the decisions in outputs/auditor-comments.md and mark the register as a revision. "
                "Then run `.venv/bin/python .claude/skills/audit-program/build_pack.py --gate` and report its output."),
     "produces": ["outputs/risk-register.md"]},
    {"id": "team", "title": "Plan, challenge and check", "kind": "Agent team", "who": "planner, challenger, qa-reviewer",
     "prompt": ("Run the agent team for the audit planning pack, following the lead procedure in CLAUDE.md. "
                "This session is headless, so teammates run as named sub-agents: launch planner, challenger and "
                "qa-reviewer together with the Agent tool, each with subagent_type equal to its agent file name, "
                "name set to the same word, and run_in_background true, so they can message each other by name with "
                "SendMessage. Tell each one the other two names and that the gate is closed. The planner starts at once; "
                "the challenger and the qa-reviewer wait for its PACK READY v1. Let them work through the challenge rounds "
                "and the QA checks without relaying for them. When you have PLANNER DONE, CHALLENGER DONE and QA DONE, "
                "stop them and report for sign-off as CLAUDE.md says, in under 300 words."),
     "produces": ["outputs/planning-memo.md", "outputs/risk-control-matrix.md", "outputs/audit-program.md",
                  "outputs/challenges.md", "outputs/review.md"]},
    {"id": "signoff", "title": "Sign-off", "kind": "Human gate", "who": "you",
     "human": True, "produces": ["outputs/review.md"]},
]
STAGE_IDS = [s["id"] for s in STAGES]
FIRST_HALF = ["rules", "analysis", "register"]
SECOND_HALF = ["revision", "team"]

APPEND = """You are running headless inside a web harness that executes the
procurement audit planning system in this folder. No person is attached to
this session: never ask a question or wait for an answer, and never use
AskUserQuestion. Where CLAUDE.md says stop and report, stop and report.
Sub-agents are defined in .claude/agents and skills in .claude/skills. Use the
project's Python at .venv/bin/python. Keep your own messages short."""


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


class Run:
    def __init__(self, rid: str):
        self.id = rid
        self.dir = RUNS / rid
        self.ws = self.dir / "workspace"
        self.state_path = self.dir / "state.json"
        self.events_path = self.dir / "events.jsonl"

    # ---- state
    def state(self) -> dict:
        return json.loads(self.state_path.read_text())

    def save(self, st: dict):
        tmp = self.state_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(st, indent=1))
        tmp.replace(self.state_path)

    def update(self, **kw):
        st = self.state()
        st.update(kw)
        self.save(st)
        return st

    def set_stage(self, sid, **kw):
        st = self.state()
        st["stages"][sid].update(kw)
        self.save(st)

    def event(self, **ev):
        ev.setdefault("t", now())
        with self.events_path.open("a") as f:
            f.write(json.dumps(ev) + "\n")

    # ---- creation
    @classmethod
    def create(cls, label: str = "") -> "Run":
        rid = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:4]
        run = cls(rid)
        run.dir.mkdir(parents=True)
        shutil.copytree(TEMPLATE, run.ws, symlinks=True)
        (run.ws / "outputs").mkdir(exist_ok=True)
        venv = Path(os.environ.get("PROJECT_VENV", "/app/project-venv"))
        if venv.exists() and not (run.ws / ".venv").exists():
            (run.ws / ".venv").symlink_to(venv)
        run.save({"id": rid, "label": label, "created": now(), "status": "running", "current": "rules",
                  "cost_usd": 0.0, "model": MODEL,
                  "stages": {s["id"]: {"status": "pending"} for s in STAGES}})
        run.event(kind="run", text=f"Run {rid} created; workspace copied from the Part A project.")
        return run


TEAM = ("planner", "challenger", "qa-reviewer")


def team_agents(ws: Path) -> dict:
    """The three team agent files, with SendMessage added to their tools.

    In an interactive terminal Claude Code adds SendMessage to every teammate.
    Headless sessions run teammates as named sub-agents, which only get the
    tools their file lists, so the harness adds the messaging tool the same
    way. Everything else (instructions, tools, memory) comes from the files."""
    out = {}
    for name in TEAM:
        text = (ws / ".claude" / "agents" / f"{name}.md").read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
        front, body = (m.group(1), m.group(2)) if m else ("", text)
        meta = dict(re.findall(r"^(\w[\w-]*):\s*(.*)$", front, re.M))
        tools = [t.strip() for t in meta.get("tools", "").split(",") if t.strip()]
        out[name] = AgentDefinition(description=meta.get("description", name), prompt=body.strip(),
                                    tools=tools + ["SendMessage"], memory=meta.get("memory") or None,
                                    model=MODEL)
    return out


async def run_stage(run: Run, stage: dict):
    """One Claude Code session in the run's workspace, streaming its activity to events.jsonl."""
    sid = stage["id"]
    run.set_stage(sid, status="running", started=now())
    run.update(current=sid, status="running")
    run.event(kind="stage", stage=sid, text=f"{stage['title']} ({stage['kind']}: {stage['who']})")
    run.event(kind="prompt", stage=sid, text=stage["prompt"])
    names = {}  # Agent tool_use id -> sub-agent label
    opts = ClaudeAgentOptions(
        cwd=str(run.ws),
        setting_sources=["project"],
        model=MODEL,
        system_prompt={"type": "preset", "preset": "claude_code", "append": APPEND},
        permission_mode="dontAsk",
        allowed_tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep", "Agent", "Skill",
                       "SendMessage", "TaskStop", "TodoWrite"],
        disallowed_tools=["WebFetch", "WebSearch", "AskUserQuestion"],
        max_budget_usd=STAGE_BUDGET,
        agents=team_agents(run.ws) if sid == "team" else None,
        env={"CLAUDE_CODE_SUBAGENT_MODEL": MODEL, "CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH": "1",
             "CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS": "4", "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"},
    )
    t0 = time.time()
    result = None
    try:
        async for msg in query(prompt=stage["prompt"], options=opts):
            who = names.get(getattr(msg, "parent_tool_use_id", None) or "", "lead")
            if isinstance(msg, AssistantMessage):
                for b in msg.content:
                    if isinstance(b, TextBlock) and b.text.strip():
                        run.event(kind="text", stage=sid, who=who, text=b.text[:4000])
                    elif isinstance(b, ToolUseBlock):
                        if b.name in ("Agent", "Task"):
                            label = b.input.get("name") or b.input.get("subagent_type") or "sub-agent"
                            names[b.id] = label
                            run.event(kind="spawn", stage=sid, who=who, text=f"starts {label}",
                                      detail=(b.input.get("prompt") or "")[:600])
                        else:
                            run.event(kind="tool", stage=sid, who=who, text=describe_tool(b))
            elif isinstance(msg, UserMessage) and isinstance(msg.content, list):
                for b in msg.content:
                    if isinstance(b, ToolResultBlock) and b.is_error:
                        txt = b.content if isinstance(b.content, str) else json.dumps(b.content)[:300]
                        run.event(kind="tool_error", stage=sid, who=who, text=str(txt)[:300])
            elif isinstance(msg, ResultMessage):
                result = msg
    except Exception as e:  # the SDK raises after an error result; keep what was captured
        run.event(kind="error", stage=sid, text=f"{type(e).__name__}: {str(e)[:500]}")
    cost = float(getattr(result, "total_cost_usd", 0) or 0)
    st = run.state()
    st["cost_usd"] = round(st.get("cost_usd", 0) + cost, 4)
    run.save(st)
    ok = result is not None and not result.is_error and all((run.ws / p).exists() for p in stage["produces"])
    missing = [p for p in stage["produces"] if not (run.ws / p).exists()]
    run.set_stage(sid, status="done" if ok else "failed", finished=now(), seconds=round(time.time() - t0),
                  cost_usd=round(cost, 4), turns=getattr(result, "num_turns", None),
                  result=(getattr(result, "result", "") or "")[:6000], missing=missing)
    run.event(kind="result", stage=sid, ok=ok, text=(getattr(result, "result", "") or "")[:6000],
              cost_usd=round(cost, 4), seconds=round(time.time() - t0))
    if not ok:
        why = f"missing {', '.join(missing)}" if missing else (getattr(result, "subtype", None) or "no result")
        run.update(status="failed", error=f"{stage['title']} failed: {why}")
    return ok


def describe_tool(b: ToolUseBlock) -> str:
    i = b.input or {}
    if b.name == "Bash":
        return f"$ {str(i.get('command', ''))[:300]}"
    if b.name in ("Read", "Write", "Edit"):
        return f"{b.name} {i.get('file_path', '')}"
    if b.name == "Skill":
        return f"skill {i.get('skill', '')}"
    if b.name == "SendMessage":
        return f"message to {i.get('to', '')}: {str(i.get('message', i.get('content', '')))[:240]}"
    if b.name in ("Glob", "Grep"):
        return f"{b.name} {i.get('pattern', '')}"
    return b.name


async def run_stages(run: Run, ids):
    for sid in ids:
        stage = next(s for s in STAGES if s["id"] == sid)
        if not await run_stage(run, stage):
            return False
    return True


async def first_half(run: Run):
    if await run_stages(run, FIRST_HALF):
        run.set_stage("gate", status="waiting")
        run.update(status="awaiting_gate", current="gate")
        run.event(kind="gate", text="Register ready. Waiting for the auditor's decisions.")


async def second_half(run: Run):
    if await run_stages(run, SECOND_HALF):
        run.set_stage("signoff", status="waiting")
        run.update(status="awaiting_signoff", current="signoff")
        run.event(kind="gate", text="Pack ready. Waiting for the auditor's sign-off.")


# ---- the two human gates are written by code, not by the model

def register_rows(ws: Path):
    p = ws / "outputs" / "risk-register.md"
    rows, on = [], False
    if not p.exists():
        return rows
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            on = line.strip() == "## Summary"
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if on and len(cells) >= 9 and re.fullmatch(r"R-\d+", cells[0]):
            rows.append({"id": cells[0], "title": cells[1], "L": cells[2], "I": cells[3], "score": cells[4],
                         "label": cells[5], "band": cells[6], "fig4": cells[7], "scope": cells[8]})
    return rows


def write_decisions(run: Run, reviewer: str, decisions: dict):
    p = run.ws / "outputs" / "auditor-comments.md"
    text = p.read_text(encoding="utf-8")
    today = datetime.date.today().isoformat()
    text = re.sub(r"^Reviewer:.*$", f"Reviewer: {clean(reviewer)}", text, count=1, flags=re.M)
    text = re.sub(r"^Date:.*$", f"Date: {today}", text, count=1, flags=re.M)
    out = []
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 6 and re.fullmatch(r"R-\d+", cells[0]) and cells[0] in decisions:
            d = decisions[cells[0]]
            cells[4] = d["decision"]
            cells[5] = clean(d.get("comment", ""))
            line = "| " + " | ".join(cells[:6]) + " |"
        out.append(line)
    p.write_text("\n".join(out) + "\n", encoding="utf-8")
    run.set_stage("gate", status="done", finished=now(), reviewer=clean(reviewer))
    run.event(kind="gate", text=f"Decisions recorded by {clean(reviewer)}: " +
              ", ".join(f"{k} {v['decision']}" for k, v in decisions.items()))


def write_signoff(run: Run, name: str, decision: str, comment: str):
    p = run.ws / "outputs" / "review.md"
    text = p.read_text(encoding="utf-8")
    today = datetime.date.today().isoformat()
    reps = [(r"^Signed off by:.*$", f"Signed off by: {clean(name)}"), (r"^Date:[ \t]*$", f"Date: {today}"),
            (r"^Decision \(sign off / return to the team\):.*$", f"Decision (sign off / return to the team): {decision}"),
            (r"^Comment:.*$", f"Comment: {clean(comment)}")]
    block_at = text.find("## Auditor sign-off")
    head, block = (text[:block_at], text[block_at:]) if block_at >= 0 else (text + "\n\n", "## Auditor sign-off\n\nSigned off by:\nDate:\nDecision (sign off / return to the team):\nComment:\n")
    for pat, rep in reps:
        block = re.sub(pat, rep, block, count=1, flags=re.M)
    p.write_text(head + block, encoding="utf-8")
    run.set_stage("signoff", status="done", finished=now(), by=clean(name), decision=decision)
    run.update(status="signed_off" if decision == "sign off" else "returned", current="signoff")
    run.event(kind="gate", text=f"{clean(name)} recorded: {decision}.")


def clean(s: str) -> str:
    return re.sub(r"[|\r\n]+", " ", str(s or "")).strip()[:500]
