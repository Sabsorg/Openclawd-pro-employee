"""Tests for the Memory module."""

from openclawd_employee.memory import Memory


class TestMemory:
    def test_add_and_conversation(self) -> None:
        mem = Memory()
        mem.add("user", "hello")
        mem.add("assistant", "hi")
        assert len(mem.conversation) == 2
        assert mem.conversation[0].role == "user"

    def test_system_prompt_in_init(self) -> None:
        mem = Memory(system_prompt="You are helpful.")
        assert len(mem.conversation) == 1
        assert mem.conversation[0].role == "system"

    def test_to_messages(self) -> None:
        mem = Memory()
        mem.add("user", "ping")
        msgs = mem.to_messages()
        assert msgs == [{"role": "user", "content": "ping"}]

    def test_to_messages_with_tool_call_id(self) -> None:
        """tool-result messages must include tool_call_id."""
        mem = Memory()
        mem.add("tool", "result text", tool_call_id="call_abc")
        msgs = mem.to_messages()
        assert len(msgs) == 1
        assert msgs[0]["role"] == "tool"
        assert msgs[0]["tool_call_id"] == "call_abc"
        assert msgs[0]["content"] == "result text"

    def test_to_messages_with_tool_calls(self) -> None:
        """assistant messages that triggered tools must include tool_calls."""
        tc = [{"id": "call_1", "function": {"name": "echo", "arguments": "{}"}}]
        mem = Memory()
        mem.add("assistant", "", tool_calls=tc)
        msgs = mem.to_messages()
        assert len(msgs) == 1
        assert msgs[0]["role"] == "assistant"
        assert msgs[0]["tool_calls"] == tc

    def test_store_and_get_fact(self) -> None:
        mem = Memory()
        mem.store_fact("project", "openclawd")
        assert mem.get_fact("project") == "openclawd"
        assert mem.get_fact("missing", "default") == "default"

    def test_facts_property(self) -> None:
        mem = Memory()
        mem.store_fact("a", "1")
        mem.store_fact("b", "2")
        assert mem.facts == {"a": "1", "b": "2"}

    def test_clear(self) -> None:
        mem = Memory(system_prompt="sys")
        mem.store_fact("k", "v")
        mem.clear()
        assert len(mem.conversation) == 0
        assert mem.facts == {}
