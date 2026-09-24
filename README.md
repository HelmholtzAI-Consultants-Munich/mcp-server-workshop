# From MCP Server to Agent

**A Hands-On Workshop on Building Tool-Using LLM Systems**

You will build a small research assistant over local PDFs: write your own MCP
server, then connect it to a language model so the model can choose and call
your tools on its own.

**Date:** Friday 25 September 2026, 09:30 to 15:30
**Location:** in person, Neuherberg campus, NHB31, Room 3

**Slides and overview:** [Helmholtz-AI-Matter/agentic-ai-workshop](https://github.com/Helmholtz-AI-Matter/agentic-ai-workshop)

---



## Before the workshop

Please arrive with the repository cloned and the environment working. It takes
about ten minutes and there is very little time for it on the day.

**You do not need an API key in advance.** A key is provided and configured
during the workshop, so there is nothing to register for beforehand.

### Requirements

- **Python 3.11 or higher** (3.11 and 3.12 are tested)
- git
- Roughly 200 MB of disk space

Check your version first:

```bash
python3 --version
```

If it is older than 3.11, install a newer one from
[python.org](https://www.python.org/downloads/) or through conda below.

### 1. Clone the repository

```bash
git clone https://github.com/HelmholtzAI-Consultants-Munich/mcp-server-workshop.git
cd mcp-server-workshop
```



### 2. Create the environment

With conda:

```bash
conda env create -f environment.yml
conda activate mcp-server-workshop
```

Or with venv, if you do not use conda:

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```



### 3. Check that it works

```bash
bash check_install.sh
```

This verifies your Python version, the dependencies, the sample data and tool
discovery. It needs no API key and no network. If everything passes, you are
ready.

You can also look at the tools that ship with the project:

```bash
python call_tool.py --list
```

Run every command from the project root, the folder containing `run_bot.py`.
Otherwise you will see `ModuleNotFoundError: No module named 'agent'`.

### Bring your own data (optional)

Sample PDFs are included, so you do not need to bring anything. If you have
PDFs you would rather experiment with, copy them into `data/` and the tools
will pick them up.

---



## Schedule


| Time          | Session                                                           | Facilitator |
| ------------- | ----------------------------------------------------------------- | ----------- |
| 09:30 – 09:45 | Welcome and introduction                                          | Haider      |
| 09:45 – 10:30 | Introduction to agentic AI and MCP                                | Haider      |
| 10:30 – 10:45 | Q&A                                                               |             |
| 10:45 – 11:00 | The task, the repository, and group formation                     | Ema         |
| 11:00 – 11:15 | Break                                                             |             |
| 11:15 – 11:30 | Setup and API key                                                 | Haider      |
| 11:30 – 12:30 | **Core task 1** — your own MCP server, and a look at the solution |             |
| 12:30 – 13:30 | Lunch                                                             |             |
| 13:30 – 15:00 | **Core task 2** — the adapter, then an optional extension         | Haider, Ema |
| 15:00 – 15:15 | Group presentations                                               | Haider      |
| 15:15 – 15:30 | Wrap-up                                                           | Haider, Ema |


Core task 1 gets the morning slot, core task 2 the afternoon. Extensions are
for groups who finish core task 2 with time to spare.

---



## What you will build

Two core tasks, in order. **Both are the point of the day.** Everything else is
optional.

### Core task 1: your own MCP server

File: `mcp_servers/research_server.py`

Implement two tools. `save_paper_text` extracts a paper's text and saves it to
`output/`; `list_saved` reports what is there. A tool is an ordinary Python
function with `@mcp.tool()` above it, and `mcp_servers/pdf_server.py` is a
complete worked example to follow.

```bash
python -m pytest tests/test_research_server.py -q   # passes when you are done
python call_tool.py --list                          # see your tool and its schema
```

Guide: [Core task 1](docs/core-tasks/#core-task-1-build-your-own-mcp-server)

### Core task 2: connect it to the model

File: `agent/adapter.py`

Implement two functions. One converts MCP tool definitions into the format the
model's API expects; the other takes the tool call the model sends back and
routes it to the right server. The conversation loop around them is provided.

```bash
python -m pytest tests/test_adapter.py -q           # passes when you are done
python run_bot.py --agent --trace "What methods are used?"
```

Guide: [Core task 2](docs/core-tasks/#core-task-2-connect-your-tools-to-the-agent)

### Optional extensions

**Only once both core tasks work.** Pick **one**. You are not expected to do
more than one, and finishing the two core tasks is a complete result.


| Track                         | Focus                                                            | File                         |
| ----------------------------- | ---------------------------------------------------------------- | ---------------------------- |
| **A** Feature sprint          | Add a feature to your server, the pipeline or the agent          | [Track A — Feature sprint](docs/extensions/track-a-feature-sprint.md) |
| **B** Architecture planning   | Plan an agentic integration for your own project, no code        | [Track B — Architecture planning](docs/extensions/track-b-architecture-planning.md) |
| **C** Integration experiments | Probe the system, compare tools against the bot, report failures | [Track C — Integration experiments](docs/extensions/track-c-integration-experiments.md) |


Fill in the deliverable section at the bottom of your chosen file before
share-out.

---



## Running things

```bash
python call_tool.py --list                     # every tool, with its schema
python call_tool.py list_pdfs                  # call one tool directly
python run_bot.py --dry-run                    # the four-step pipeline, no key
python run_bot.py --agent --dry-run            # check your schema conversion, no key
python run_bot.py --agent --trace "..."        # the full agent, needs a key
```

Commands marked "no key" work before the API key is handed out. The rest need
the key configured in a `.env` file, which is a workshop step.

A fresh clone deliberately contains failing tests: the two core tasks are
unimplemented. Everything else should pass:

```bash
python -m pytest tests/ -m "not exercise" -q
```

---



## Layout

- `mcp_servers/` — MCP servers. Files starting with `_` are shared helpers, not servers
- `agent/` — MCP client, the adapter you write, and the supplied agent loop
- `data/` — the PDFs, sample or your own
- `output/` — what your server writes
- `tests/` — including the tests for both core tasks
- `run_bot.py`, `call_tool.py` — the two entry points
- `docs/core-tasks/` — the two mandatory tasks, completed in order
- `docs/extensions/` — optional tracks, completed after both core tasks

Optional extensions: [docs/extensions/](docs/extensions/)
