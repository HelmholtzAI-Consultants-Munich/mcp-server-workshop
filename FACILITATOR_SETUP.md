# Facilitator setup

The participant repository intentionally does not contain `solution/`. The
directory is gitignored so reference adapter code and facilitator tests cannot
be downloaded accidentally with the workshop clone.

Keep a private facilitator copy of `solution/` beside the checkout, or provide
it through the workshop's private facilitator channel. Do not force-add it to
the participant repository and do not commit it to a public branch.

From a checkout that has the private directory present, verify the reference
implementation with:

```bash
python -m pytest -q --adapter-reference solution/agent/adapter.py
```

The `--adapter-reference` option loads the reference only inside the tests;
the participant stubs in `agent/adapter.py` remain unchanged. The complete
offline suite exercises real MCP subprocesses and simulated model responses,
so it needs no API key or network connection.

To hand the reference to another facilitator, create an archive outside the
participant repository and transfer it through the private channel:

```bash
tar -czf /private/facilitator-haicon26-solution.tgz solution/
```

Extract it into the repository root on the facilitator machine. Before sharing
the participant checkout, confirm `git status --ignored --short solution/`
shows the directory ignored and `git ls-files solution/` prints nothing.

The public workshop branch contains the exercise specification and tests, but
never the completed adapter answer.
