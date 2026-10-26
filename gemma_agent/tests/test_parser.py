from gemma_agent.agent.parser import extract_actions


def test_extracts_json_tool() -> None:
    text = 'I will look now {"tool": "read_file", "arguments": {"filepath": "a.py"}}'
    actions = extract_actions(text)
    assert actions == [{"name": "read_file", "arguments": {"filepath": "a.py"}}]
