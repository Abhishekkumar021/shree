from __future__ import annotations

import argparse
from pathlib import Path

import uvicorn

from gemma_agent.agent.loop import AgentLoop, result_to_json
from gemma_agent.config.settings import get_settings
from gemma_agent.llm.llama_server import start_llama_server, stop_llama_server
from gemma_agent.logsetup import setup_logging
from gemma_agent.runtime.workspace import prepare_workspace


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="gemma-agent")
    sub = parser.add_subparsers(dest="command", required=True)

    run_p = sub.add_parser("run", help="Run the agent on an issue statement")
    run_p.add_argument("--issue", help="Issue text")
    run_p.add_argument("--issue-file", type=Path, help="Path to an issue markdown/text file")
    run_p.add_argument("--no-llama-lifecycle", action="store_true")

    serve_p = sub.add_parser("serve", help="Start the FastAPI control plane")
    serve_p.add_argument("--host", default="127.0.0.1")
    serve_p.add_argument("--port", type=int, default=8000)

    args = parser.parse_args(argv)
    setup_logging()
    settings = get_settings()
    prepare_workspace(settings)

    if args.command == "serve":
        uvicorn.run("gemma_agent.app:app", host=args.host, port=args.port, reload=False)
        return 0

    issue = args.issue
    if args.issue_file:
        issue = args.issue_file.read_text(encoding="utf-8")
    if not issue:
        parser.error("Provide --issue or --issue-file")

    manage = settings.gemma_agent_manage_llama and not args.no_llama_lifecycle
    try:
        if manage:
            start_llama_server(settings)
        result = AgentLoop(settings).run(issue)
        print(result_to_json(result))
        return 0 if result.error is None else 1
    finally:
        if manage:
            stop_llama_server()
