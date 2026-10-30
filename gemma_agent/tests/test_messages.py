from gemma_agent.llm.messages import expand_tool_calls, flatten_tool_calls, for_llama_server


def test_expand_adds_function_type() -> None:
    expanded = expand_tool_calls(
        [{"id": "abc", "name": "read_file", "arguments": {"filepath": "."}}]
    )
    assert expanded == [
        {
            "id": "abc",
            "type": "function",
            "function": {
                "name": "read_file",
                "arguments": '{"filepath": "."}',
            },
        }
    ]


def test_llama_messages_include_tool_call_type() -> None:
    messages = for_llama_server(
        [
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {"id": "abc", "name": "read_file", "arguments": {"filepath": "."}}
                ],
            },
            {
                "role": "tool",
                "tool_call_id": "abc",
                "name": "read_file",
                "content": "ok",
            },
        ]
    )
    assert messages[0]["tool_calls"][0]["type"] == "function"
    assert messages[0]["content"] is None
    assert messages[1] == {
        "role": "tool",
        "tool_call_id": "abc",
        "content": "ok",
    }


def test_flatten_round_trip() -> None:
    expanded = expand_tool_calls(
        [{"id": "x", "name": "list_dir", "arguments": {"path": "."}}]
    )
    assert flatten_tool_calls(expanded) == [
        {"id": "x", "name": "list_dir", "arguments": {"path": "."}}
    ]
