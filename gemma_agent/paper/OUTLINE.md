# Paper Track outline (max 3,000 words)

Target: [Google - The Gemma 4 Developer Agent Paper Track](https://www.kaggle.com/competitions/gemma-4-developer-agent-paper)

Deadline: 12 November 2026, 23:59 UTC

Working title: Guardrailed local software-engineering agents for consumer-hardware Gemma 4

## Abstract

Local coding agents fail less from missing APIs than from unbounded tools, weak repository navigation, and no test-gated stop condition. This project treats the agent as a jailed SWE loop: file tools plus code/test execution only, budgeted steps, and an ADK-compatible submission layout that can later consume competition code-graphs.

## Introduction

Cloud SWE agents assume a large model and an open shell. The competition requires the opposite: Gemma 4 on one accelerator, no internet, and patches that pass hidden tests. The research question is whether a small local model becomes more reliable when the action space is reduced to code edits and pytest, with path and command policies enforced outside the model.

## Methods

- Modular agent loop with planner / navigator / coder / reviewer prompts
- Tool jail: workspace path policy, allowlisted binaries, no shell chaining
- Local llama.cpp OpenAI-compatible server (Gemma 4 E4B GGUF)
- Graph/embedding tool stubs that swap in competition neighbors without changing the loop
- Trace logging for verifiability

## Experiments (to fill)

- Ablate shell access vs code-only execution
- Ablate graph tools vs grep/read only
- Measure pass@k on a public subset (fastapi / rich / requests / httpx style tasks)
- Report step budget, wall time, and patch size

## Related work

SWE-bench, SWE-agent, ADK agent config, repository graph retrieval, PEFT/LoRA for tool use.

## Submission notes

Writeup must include title, abstract, introduction, methods/experiments, related work. Optional public notebook. One writeup can be considered for Best Paper / Best Resource / Best Application but can win only one.
