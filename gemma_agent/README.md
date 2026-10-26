# Gemma 4 developer agent

Local software-engineering agent for the [Gemma 4 Developer Agent](https://www.kaggle.com/competitions/gemma-4-developer-agent) and [Paper Track](https://www.kaggle.com/competitions/gemma-4-developer-agent-paper).

This tree is independent of the existing `src/bugloc` experiment. It talks to the same kind of local `llama-server` (OpenAI-compatible) and Gemma 4 E4B GGUF you already use.

## Layout

```
gemma_agent/
  configs/                 runtime, model profiles, guardrails
  src/gemma_agent/         Python package
    agent/                 SWE loop + JSON tool-call fallback
    guardrails/            path jail, code-only shell, budgets
    llm/                   llama-server lifecycle + OpenAI client
    tools/                 harness-shaped tools (files, tests, patch, graph stubs)
    runtime/               workspace bootstrap
    eval/                  task records (expand later)
  submission/              Kaggle ADK zip layout (agent.yaml at root)
  paper/                   paper-track outline
  tests/
  scripts/pack_submission.py
  workspace/               jailed working copy
```

Swap graph/embedding backends later without changing the loop: implement the bodies in `tools/graph.py`.

## Guardrails

The agent cannot have a free terminal.

- Commands are parsed as argv (`shell=False`).
- Only `python` / `pytest` / `ruff` binaries.
- No `python -c`, chaining (`&&`, `|`, `;`), network, installs, or path escape.
- Reads/writes stay under `workspace/` with extension and deny-name checks.
- Step, shell, write, and patch-size budgets are enforced in process.

Local `run_code` maps to the competition `run_command` tool, but this runtime is stricter on purpose.

## Configure llama.cpp

Copy `.env.example` to `.env` and point at your install:

```
LLAMA_SERVER=C:\llama\llama-server.exe
MODEL_PATH=C:\llama\models\gemma-4-E4B_q4_0-it.gguf
LLAMA_HOST=127.0.0.1
LLAMA_PORT=8080
LLM_BASE_URL=http://127.0.0.1:8080/v1
```

The server is started with `--jinja`, context `4096`, and `6` threads, matching the existing local setup.

If llama-server is already up, set `GEMMA_AGENT_MANAGE_LLAMA=false`.

## Run

From this directory, using the existing Python 3.12 environment:

```
python -m gemma_agent run --issue "Describe the bug"
python -m gemma_agent serve
python scripts/pack_submission.py
python -m pytest tests
```

`PYTHONPATH=src` is required unless the package is installed editable.

## Competition notes

- Main track zip must contain `agent.yaml` at the archive root. Use `scripts/pack_submission.py`.
- Every agent/sub-agent must share one Gemma 4 variant. Default here is E4B (small-model prize eligible).
- Paper track: 3,000-word Kaggle Writeup by 12 November 2026 23:59 UTC. Start from `paper/OUTLINE.md`.
