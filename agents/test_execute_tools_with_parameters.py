from agents.execute_tools_with_parameters import parse_tool_call_from_content
import pytest


def test_parse_tool_call_from_content():
    # Test case 1: Simple tool call
    content = '<|python_start|>{"type": "function", "name": "nth_prime", "parameters": {"n": 10}}<|python_end|>"'
    expected = {
        "name": "nth_prime",
        "args": {"n": 10},
        "type": "function",
        "id": "0",
    }
    actual = parse_tool_call_from_content(content)
    for key, val in expected.items():
        assert actual[0][key] == val
