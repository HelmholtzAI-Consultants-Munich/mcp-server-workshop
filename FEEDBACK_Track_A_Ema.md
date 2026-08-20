# Track A feedback for Haider & Karol

Feedback after going through the hackathon as a participant would: set it up from
scratch, ran the baseline, then picked one Track A backlog task (**A5**) and
implemented it. Validated the whole flow on both Python 3.11 and 3.12.

**Overall:** the concept is good and the material is close to ready. The code is
clean, the tracks are well thought out, and the docs are friendly. There is **one
showstopper** that will block a fresh install, plus a few accessibility improvements
that would make a big difference for a course audience.

---

## TL;DR (in priority order)

| Priority | Issue | Fix |
|---|---|---|
| 🔴 Must fix | Fresh install pulls **mcp 2.0**, which removed `FastMCP`; both servers crash with a cryptic `Connection closed` | Pin **`mcp>=1.0.0,<2.0.0`** in `requirements.txt` |
| 🟠 Should fix | Setup is **conda-only** and pins Python 3.12; no fallback | Add a `venv` + `pip` path to the README (works on 3.11 and 3.12) |
| 🟠 Should fix | Backlog task **A1 asks to build `search_pdf_text`, but it already exists** | Remove A1 or reframe it (e.g. cross-file search / ranking) |
| 🟠 Should fix | **No simple way to test a new tool** after adding it | Add a `call_tool.py NAME '{json}'` helper or a `--tool` flag |
| 🟢 Nice | A per-task "how to test your change" line | One line under each backlog item |

---

## 1. Understandability of the task

**Good.** `PARTICIPANT_SHEET.md`, `TRACKS.md` and `FEATURE_BACKLOG_Track_A.md` are
clear and well scoped. The four-step pipeline (Discover, Select, Read, Answer) is easy
to grasp, and the backlog table with sizes (S/M/L) and "no API key needed" flags is
genuinely helpful for picking a task quickly.

**One real snag:** task **A1 ("implement `search_pdf_text`")** is confusing, because
that tool **already exists** in `mcp_servers/pdf_server.py` (lines 77 to 98). A
participant who opens the file to start A1 finds it already done. Suggest either
dropping A1, or reframing it into a genuinely new task (for example: search across
*all* PDFs at once instead of one file, or add relevance ranking).

## 2. Accessibility of the material

**🔴 The one that will actually block people: the mcp version.**
`requirements.txt` pins only `mcp>=1.0.0`. A fresh install today resolves to
**mcp 2.0.0**, which **removed the `mcp.server.fastmcp` module** that both MCP servers
import. The servers then crash on startup and the bot fails with:

```
mcp.shared.exceptions.MCPError: Connection closed
```

There is no hint that the cause is a dependency version, so a participant would be
stuck within the first 10 minutes. **Fix: pin `mcp>=1.0.0,<2.0.0`** (verified: 1.29.0
works end to end). It is worth pinning the other dependencies too, to avoid the same
class of surprise later.

*Reproduce:* fresh env, `pip install -r requirements.txt`, `python run_bot.py --dry-run`.

**🟠 Setup assumes conda and pins Python 3.12.** The only documented path is
`conda env create -f environment.yml`, and the env pins Python 3.12. That is fine for
anyone with conda, but a participant without it has no fallback. A few lines in the
README for a plain `venv` would widen access a lot:

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

(Confirmed the project runs on both 3.11 and 3.12, so the Python version itself is not
a blocker; see section 4.)

**🟠 No easy way to test a new tool.** Adding an MCP tool is the heart of Track A, but
once you add one there is no simple way to *call* it: `run_bot.py` only runs the fixed
four-step pipeline, which does not touch a new tool. To test my A5 tool I had to write
my own async `MCPClient` harness. A participant without an async/MCP background will be
stuck at "I added my tool… now how do I run it?" A tiny helper would close this gap,
e.g. `python call_tool.py list_papers '{}'`, or a `--tool NAME` flag on the CLI.

**🟢 Nice touches.** The repeated "run from the project root" warnings and the
no-API-key `--dry-run` path are thoughtful and prevent common first-run errors.

## 3. Complexity (relative to my coding expertise)

The **amount** of code is small (~130 lines) and readable, and implementing a backlog
task is quick for someone comfortable with Python: for A5 I mirrored an existing tool,
reused the `safe_pdf_path` helper, and added ~20 lines.

The **conceptual** load is the real hurdle, though: MCP client/server, async/await, and
stdio subprocesses. Someone with "some programming knowledge" but no exposure to these
will need guidance both to understand the architecture and to test their change. This
matches the meeting's read that, as a guided course session, it is closer to 3 to 4 hours
than a 1 to 1.5 hour open hackathon. Two things would help most: a short guided intro to
MCP with one worked example task before people start, and the tool-test helper above.

## 4. Python 3.12 (since you are standardizing on it)

Confirmed: the full flow runs on **Python 3.12.13** (install, baseline `--dry-run`, my
A5 tool, and the check script), all green, and cleaner than 3.11 since 3.12 is the
version the repo already targets. Important nuance: the **mcp pin is still required**
on 3.12. The mcp 2.0 breakage is a package-version issue, not a Python-version issue,
so it happens on any interpreter. Net: standardizing on 3.12 is fine, but the real
blocker to a clean first run is the unpinned `mcp`, not the Python version.

## 5. What I built while testing (attached in the repo)

- **`check_install.sh`** is a no-API-key preflight check that verifies the project root,
  Python, all dependencies **including the mcp/`FastMCP` check**, the sample PDFs, and
  then runs `--dry-run`. Every failure prints an actionable fix, and it exits non-zero
  (CI-friendly). This turns the mcp trap from a cryptic dead end into a one-line,
  self-explanatory failure.
- **Example Track A solution (A5):** a `list_papers` MCP tool in `pdf_server.py` plus
  `papers/manifest.json`, as a worked reference (curated metadata, flags whether each
  file is present).

## Bottom line

Strong material, minimal adaptation needed. Before anyone runs it: **pin mcp to
`<2.0.0`**, add a `venv`/`pip` fallback and a small tool-test helper, and fix the A1
overlap. Plan for a guided 3 to 4 hour session rather than an open hackathon. Happy to
walk through any of this with Haider.
