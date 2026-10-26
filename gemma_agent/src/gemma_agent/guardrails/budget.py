from dataclasses import dataclass

from gemma_agent.guardrails.errors import GuardrailError


@dataclass
class Budget:
    max_steps: int
    max_shell_calls: int
    max_file_writes: int
    max_patch_bytes: int
    steps: int = 0
    shell_calls: int = 0
    file_writes: int = 0

    def consume_step(self) -> None:
        self.steps += 1
        if self.steps > self.max_steps:
            raise GuardrailError(f"Step budget exhausted ({self.max_steps})")

    def consume_shell(self) -> None:
        self.shell_calls += 1
        if self.shell_calls > self.max_shell_calls:
            raise GuardrailError(f"Shell budget exhausted ({self.max_shell_calls})")

    def consume_write(self) -> None:
        self.file_writes += 1
        if self.file_writes > self.max_file_writes:
            raise GuardrailError(f"Write budget exhausted ({self.max_file_writes})")

    def snapshot(self) -> dict[str, int]:
        return {
            "steps": self.steps,
            "max_steps": self.max_steps,
            "shell_calls": self.shell_calls,
            "max_shell_calls": self.max_shell_calls,
            "file_writes": self.file_writes,
            "max_file_writes": self.max_file_writes,
        }
