# Built from the repo root: fly deploy --config deploy/fly.toml
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends poppler-utils git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY deploy/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# The project's own Python (what the agents call as .venv/bin/python)
COPY requirements.txt /app/template-requirements.txt
RUN python -m venv /app/project-venv && /app/project-venv/bin/pip install --no-cache-dir -r /app/template-requirements.txt

# The Part A system, copied into a fresh workspace for every run
COPY CLAUDE.md /app/template/CLAUDE.md
COPY .claude /app/template/.claude
COPY data /app/template/data
COPY scripts /app/template/scripts
COPY requirements.txt /app/template/requirements.txt

# The Part A run, shown read-only as the reference run
COPY deploy/reference /app/reference
COPY deploy/app /app/app

RUN useradd -m -u 1000 agent && mkdir -p /data/runs && chown -R agent:agent /data /app
USER agent
ENV HOME=/home/agent TEMPLATE_DIR=/app/template RUNS_DIR=/data/runs REFERENCE_DIR=/app/reference \
    PROJECT_VENV=/app/project-venv PYTHONUNBUFFERED=1
EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--proxy-headers"]
