# Openclawd Pro Employee

> An autonomous AI agent framework that gives your Openclawd employee agentic capability to accomplish **any** workflow.

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## What Is This?

**Openclawd Pro Employee** turns a plain LLM into a fully autonomous *employee* that can plan, act, observe, and iterate until a task is done. It follows the **ReAct** (Reason + Act) pattern:

1. **Plan** — the agent breaks the task into steps.
2. **Act** — it calls the right tool (shell, file I/O, HTTP, Python, etc.).
3. **Observe** — it reads the tool output and decides what to do next.
4. **Repeat** — the loop continues until the task is complete or the iteration limit is reached.

It ships with a set of built-in tools, a workflow engine with dependency management, short-term and long-term memory, and pluggable LLM providers (OpenAI, Anthropic, or any compatible API).

---

## Features

| Capability | Details |
|---|---|
| **ReAct Agent Loop** | Autonomous plan → act → observe cycle with configurable iteration limits |
| **Built-in Tools** | File read/write, directory listing, shell commands, HTTP requests, Python code execution |
| **Custom Tools** | Extend the agent by subclassing `Tool` and registering it |
| **Workflow Engine** | Define multi-step workflows with dependency ordering |
| **Memory** | Short-term conversation history + long-term key-value fact store |
| **Multi-Provider LLM** | OpenAI and Anthropic out of the box; easy to add more |
| **CLI** | One-shot tasks or an interactive REPL session |
| **Tool Filtering** | Restrict which tools an agent instance can use via config |

---

## Architecture

```
┌──────────────────────────────────────────────────┐
│                    CLI / Caller                   │
└────────────────────────┬─────────────────────────┘
                         │
                   ┌─────▼─────┐
                   │   Agent   │  ReAct loop
                   └─────┬─────┘
            ┌────────────┼────────────┐
            │            │            │
      ┌─────▼─────┐ ┌───▼────┐ ┌────▼─────┐
      │  Planner  │ │ Memory │ │ Executor │
      └───────────┘ └────────┘ └────┬─────┘
                                    │
                            ┌───────▼───────┐
                            │ Tool Registry │
                            └───────┬───────┘
               ┌────────┬───────┬───┴────┬──────────┐
               │        │       │        │          │
          read_file write_file shell http_request python_exec
```

### Key Modules

| Module | Purpose |
|---|---|
| `agent.py` | Core ReAct loop — orchestrates planning, tool use, and observation |
| `planner.py` | Asks the LLM to decompose a goal into discrete steps |
| `executor.py` | Dispatches tool calls and collects results |
| `memory.py` | Conversation history (short-term) and fact store (long-term) |
| `config.py` | Dataclass-based configuration for the agent and LLM provider |
| `cli.py` | Command-line interface for one-shot and interactive use |
| `tools/` | Built-in tools (file, shell, web, code) and the `Tool` / `ToolRegistry` base classes |
| `workflows/` | Multi-step workflow engine with dependency resolution |
| `llm/` | Provider-agnostic LLM interface with OpenAI and Anthropic implementations |

---

## Quick Start

### 1. Install

```bash
# Clone the repository
git clone https://github.com/Sabsorg/Openclawd-pro-employee.git
cd Openclawd-pro-employee

# Install in editable mode (with dev dependencies for testing)
pip install -e ".[dev]"
```

### 2. Set Your API Key

```bash
# For OpenAI (default)
export OPENAI_API_KEY="sk-..."

# For Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."
```

### 3. Run a Task

```bash
# One-shot task
openclawd-employee "List all Python files in the current directory and count them"

# Interactive mode
openclawd-employee --interactive
```

### 4. Use from Python

```python
import asyncio
from openclawd_employee.agent import Agent
from openclawd_employee.config import AgentConfig, LLMConfig

config = AgentConfig(
    llm=LLMConfig(provider="openai", model="gpt-4o"),
    max_iterations=30,
)
agent = Agent(config)

result = asyncio.run(agent.run("Create a hello.txt file that says 'Hello, World!'"))
print(result)
```

---

## Built-in Tools

| Tool | Name | Description |
|---|---|---|
| 📖 Read File | `read_file` | Read the contents of any file |
| ✏️ Write File | `write_file` | Create or overwrite a file (auto-creates directories) |
| 📁 List Directory | `list_directory` | List files and sub-directories |
| 🐚 Shell | `shell` | Execute any shell command (with timeout) |
| 🌐 HTTP Request | `http_request` | Make GET/POST/PUT/DELETE/PATCH requests |
| 🐍 Python Exec | `python_exec` | Run Python code snippets and capture output |

---

## Creating Custom Tools

Extend the agent's capabilities by defining your own tools:

```python
from openclawd_employee.tools.base import Tool
from typing import Any

class GitStatusTool(Tool):
    @property
    def name(self) -> str:
        return "git_status"

    @property
    def description(self) -> str:
        return "Show the current git status of the repository."

    @property
    def parameters(self) -> dict[str, Any]:
        return {"type": "object", "properties": {}}

    async def run(self, **kwargs: Any) -> str:
        import asyncio
        proc = await asyncio.create_subprocess_shell(
            "git status --short",
            stdout=asyncio.subprocess.PIPE,
        )
        stdout, _ = await proc.communicate()
        return stdout.decode()

# Register it with an agent
agent = Agent()
agent.registry.register(GitStatusTool())
```

---

## Workflow Engine

Define explicit multi-step workflows with dependency ordering:

```python
import asyncio
from openclawd_employee.workflows import Workflow

async def fetch_data(url: str = "") -> str:
    return f"Fetched data from {url}"

async def process(data: str = "") -> str:
    return data.upper()

wf = Workflow("etl-pipeline")
wf.add_step("fetch", fetch_data, args={"url": "https://example.com/data"})
wf.add_step("process", process, args={"data": "raw"}, depends_on=["fetch"])

results = asyncio.run(wf.run())
print(results)
# {'fetch': 'Fetched data from https://example.com/data', 'process': 'RAW'}
```

---

## Configuration

All settings live in plain dataclasses — no hidden magic:

```python
from openclawd_employee.config import AgentConfig, LLMConfig

config = AgentConfig(
    name="my-employee",
    description="My custom AI employee",
    max_iterations=100,
    llm=LLMConfig(
        provider="openai",       # "openai" or "anthropic"
        model="gpt-4o",
        temperature=0.0,
        max_tokens=4096,
        base_url=None,           # Set for OpenAI-compatible APIs
    ),
    allowed_tools=["shell", "read_file", "write_file"],  # Empty = all tools
)
```

Environment variables are read automatically:

| Variable | Provider |
|---|---|
| `OPENAI_API_KEY` | OpenAI |
| `ANTHROPIC_API_KEY` | Anthropic |
| `LLM_API_KEY` | Fallback for any provider |

---

## Running Tests

```bash
pip install -e ".[dev]"
python -m pytest tests/ -v
```

All 36 tests cover the core modules: tools, registry, memory, executor, workflows, config, and agent initialization.

---

## Project Structure

```
Openclawd-pro-employee/
├── openclawd_employee/          # Main package
│   ├── __init__.py
│   ├── agent.py                 # ReAct agent loop
│   ├── cli.py                   # Command-line interface
│   ├── config.py                # Configuration dataclasses
│   ├── executor.py              # Tool call dispatcher
│   ├── memory.py                # Short-term + long-term memory
│   ├── planner.py               # LLM-based task decomposition
│   ├── llm/                     # LLM provider integrations
│   │   ├── __init__.py
│   │   ├── base.py              # Abstract provider interface
│   │   └── providers.py         # OpenAI & Anthropic implementations
│   ├── tools/                   # Built-in tool library
│   │   ├── __init__.py
│   │   ├── base.py              # Tool & ToolRegistry base classes
│   │   ├── code_tools.py        # Python execution tool
│   │   ├── file_tools.py        # File read/write/list tools
│   │   ├── shell_tools.py       # Shell command tool
│   │   └── web_tools.py         # HTTP request tool
│   └── workflows/               # Workflow orchestration
│       └── __init__.py          # Workflow & WorkflowStep classes
├── tests/                       # Unit tests
│   ├── test_agent.py
│   ├── test_code_tools.py
│   ├── test_config.py
│   ├── test_executor.py
│   ├── test_file_tools.py
│   ├── test_memory.py
│   ├── test_shell_tools.py
│   ├── test_tools.py
│   └── test_workflows.py
├── pyproject.toml               # Build & project metadata
├── requirements.txt             # Runtime dependencies
└── README.md                    # This file
```

---

## License

This project is released under the [MIT License](LICENSE).