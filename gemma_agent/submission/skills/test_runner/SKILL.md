---
name: test_runner
description: Allowed code execution patterns for this agent.
---

Allowed:
- python path/to/script.py
- python -m pytest path/to/test.py
- pytest path/to/test.py

Blocked:
- any general shell, network, package install, or destructive git command
