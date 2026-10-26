from __future__ import annotations

from typing import Any


class GetCodeNeighborsTool:
    name = "get_code_neighbors"
    description = (
        "Find incoming/outgoing neighbors of a symbol in the repo graph. "
        "Local stub until competition embeddings are wired."
    )
    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "node": {"type": "string"},
            "edge_type": {"type": "string"},
            "max_neighbors": {"type": "integer"},
        },
        "required": ["node"],
    }

    def run(
        self,
        node: str,
        edge_type: str | None = None,
        max_neighbors: int = 50,
    ) -> str:
        return (
            f"GRAPH_UNAVAILABLE: no local code-graph for {node!r} "
            f"(edge_type={edge_type}, max_neighbors={max_neighbors}). "
            "Use read_file and search instead."
        )


class SearchSimilarCodeTool:
    name = "search_similar_code"
    description = "Find similar graph nodes via embeddings. Local stub."
    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "k": {"type": "integer"},
        },
        "required": ["query"],
    }

    def run(self, query: str, k: int = 10) -> str:
        return f"EMBEDDINGS_UNAVAILABLE: cannot search {query!r} (k={k}) locally yet."


class GetCodeSubgraphTool:
    name = "get_code_subgraph"
    description = "Extract an induced subgraph for symbols. Local stub."
    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "nodes": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["nodes"],
    }

    def run(self, nodes: list[str]) -> str:
        return f"GRAPH_UNAVAILABLE: subgraph for {nodes} is not loaded locally yet."
