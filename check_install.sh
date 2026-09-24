#!/usr/bin/env bash
# check_install.sh — verify your hackathon setup before the session.
#
# Runs no LLM calls and needs no API key. It checks Python, the required
# packages (including the one version pin that matters), the sample PDFs,
# pytest, automatic server discovery, and finally runs the bot in --dry-run
# mode. Exits non-zero if anything critical fails, so it is also usable in CI.
#
# Usage:  bash check_install.sh        (run it from the project root)

# --- pretty output (plain text when not a terminal) --------------------------
if [ -t 1 ] && command -v tput >/dev/null 2>&1 && [ "$(tput colors 2>/dev/null || echo 0)" -ge 8 ]; then
  RED=$(tput setaf 1); GREEN=$(tput setaf 2); YELLOW=$(tput setaf 3); BOLD=$(tput bold); RESET=$(tput sgr0)
else
  RED=""; GREEN=""; YELLOW=""; BOLD=""; RESET=""
fi
fail=0; warn=0
ok()   { printf "  ${GREEN}OK${RESET}   %s\n" "$1"; }
bad()  { printf "  ${RED}FAIL${RESET} %s\n" "$1"; fail=$((fail + 1)); }
note() { printf "  ${YELLOW}WARN${RESET} %s\n" "$1"; warn=$((warn + 1)); }
hint() { printf "       -> %s\n" "$1"; }

printf "%s\n" "${BOLD}HAICON26 hackathon - install check${RESET}"

# --- 0. project root ---------------------------------------------------------
printf "\n%s\n" "${BOLD}Location${RESET}"
if [ -f run_bot.py ]; then
  ok "in the project root (run_bot.py found)"
else
  bad "run_bot.py not found in the current directory"
  hint "cd into the cloned haicon26-agentic-rag-hackathon folder, then re-run"
  printf "\n${RED}Cannot continue outside the project root.${RESET}\n"
  exit 1
fi

# --- 1. python ---------------------------------------------------------------
printf "\n%s\n" "${BOLD}Python${RESET}"
PYTHON=""
for c in python python3; do
  # must be on PATH *and* actually execute (skips broken pyenv/conda shims)
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys' >/dev/null 2>&1; then
    PYTHON="$c"; break
  fi
done
if [ -z "$PYTHON" ]; then
  bad "no python interpreter on PATH"
  hint "activate your environment first: conda activate hackathon-haicon"
else
  ver=$("$PYTHON" -c 'import sys;print("%d.%d.%d"%sys.version_info[:3])' 2>/dev/null)
  mm=$("$PYTHON" -c 'import sys;print("%d.%d"%sys.version_info[:2])' 2>/dev/null)
  ok "using $PYTHON ($ver)"
  case "$mm" in
    3.11 | 3.12) : ;;
    3.13) note "verified on 3.11 and 3.12; $ver usually works but is untested" ;;
    *) bad "Python $ver is too old; this project needs 3.11 or newer"
       hint "conda env create -f environment.yml && conda activate hackathon-haicon" ;;
  esac
  if [ -n "${CONDA_DEFAULT_ENV:-}" ]; then
    ok "conda env active: $CONDA_DEFAULT_ENV"
  elif [ -n "${VIRTUAL_ENV:-}" ]; then
    ok "virtualenv active: $(basename "$VIRTUAL_ENV")"
  else
    note "no conda/venv environment detected as active"
    hint "conda activate hackathon-haicon"
  fi
fi

# --- 2. dependencies ---------------------------------------------------------
printf "\n%s\n" "${BOLD}Dependencies${RESET}"
if [ -n "$PYTHON" ]; then
  for pair in "mcp:mcp" "pypdf:pypdf" "openai:openai" "dotenv:python-dotenv" "fpdf:fpdf2"; do
    mod="${pair%%:*}"; pkg="${pair##*:}"
    if "$PYTHON" -c "import $mod" 2>/dev/null; then
      ok "$pkg importable"
    else
      bad "$pkg not installed (import '$mod' failed)"
      hint "pip install -r requirements.txt"
    fi
  done
  # The pin that matters: mcp 2.0 removed mcp.server.fastmcp, which both
  # MCP servers import. Without it they crash on startup ("Connection closed").
  if "$PYTHON" -c "import mcp" 2>/dev/null; then
    mcpver=$("$PYTHON" -c "import importlib.metadata as m;print(m.version('mcp'))" 2>/dev/null)
    if "$PYTHON" -c "from mcp.server.fastmcp import FastMCP" 2>/dev/null; then
      ok "mcp $mcpver provides FastMCP"
    else
      bad "mcp $mcpver has no mcp.server.fastmcp - the MCP servers cannot start"
      hint "pip install 'mcp>=1.0.0,<2.0.0'   (and pin this in requirements.txt)"
    fi
  fi
  if "$PYTHON" -c "import pytest" 2>/dev/null; then
    ok "pytest importable"
  else
    bad "pytest not installed"
    hint "pip install -r requirements.txt"
  fi
fi

# --- 3. sample data ----------------------------------------------------------
printf "\n%s\n" "${BOLD}Sample data${RESET}"
pdfs=$(ls papers/*.pdf 2>/dev/null | wc -l | tr -d ' ')
if [ "${pdfs:-0}" -ge 1 ]; then
  ok "$pdfs sample PDF(s) in papers/"
else
  bad "no PDFs in papers/"
  hint "$PYTHON scripts/generate_sample_pdfs.py"
fi

# --- 4. api key (optional) ---------------------------------------------------
printf "\n%s\n" "${BOLD}API key${RESET} (handed out at the workshop - not needed to prepare)"
if [ -f .env ]; then
  if grep -qE '^OPENAI_API_KEY=.+' .env && ! grep -qE '^OPENAI_API_KEY=(sk-)?your-key-here' .env; then
    ok ".env present with OPENAI_API_KEY set"
  else
    note ".env present but OPENAI_API_KEY still looks like the placeholder"
    hint "add your real key to .env when you have one (not needed for --dry-run)"
  fi
else
  ok "no .env yet - nothing to do before the workshop"
  hint "the key is provided on the day; setup and both core tasks need none"
fi

# --- 4. discovery ------------------------------------------------------------
printf "\n%s\n" "${BOLD}MCP server discovery${RESET}"
if [ -n "$PYTHON" ] && [ "$fail" -eq 0 ]; then
  if out=$("$PYTHON" - <<'PY'
from agent.mcp_client import discover_server_modules
modules = discover_server_modules()
assert "mcp_servers.pdf_server" in modules
assert "mcp_servers.system_server" in modules
assert not any(module.rsplit(".", 1)[-1].startswith("_") for module in modules)
print(f"{len(modules)} server module(s) discovered")
PY
  ); then
    ok "$out"
  else
    bad "automatic MCP server discovery check failed"
    hint "run python call_tool.py --list for diagnostics"
  fi
else
  note "skipping discovery until the dependency checks pass"
fi

# --- 5. tests ----------------------------------------------------------------
printf "\n%s\n" "${BOLD}Offline tests${RESET}"
if [ -n "$PYTHON" ] && [ "$fail" -eq 0 ]; then
  if out=$("$PYTHON" -m pytest -q -m "not exercise" tests/ 2>&1); then
    ok "offline tests passed (exercises excluded)"
  else
    bad "offline discovery/PDF tests failed"
    printf '%s\n' "$out" | tail -6 | sed 's/^/       /'
  fi
else
  note "skipping offline tests until the checks above pass"
fi

# --- 6. baseline dry run -----------------------------------------------------
printf "\n%s\n" "${BOLD}Baseline${RESET} (dry run - lists PDFs, no API key)"
if [ -n "$PYTHON" ] && [ "$fail" -eq 0 ]; then
  if out=$("$PYTHON" run_bot.py --dry-run 2>&1); then
    if printf '%s' "$out" | grep -q "Step 1"; then
      ok "run_bot.py --dry-run completed and listed PDFs"
    else
      bad "run_bot.py --dry-run ran but produced unexpected output"
      printf '%s\n' "$out" | tail -3 | sed 's/^/       /'
    fi
  else
    bad "run_bot.py --dry-run failed"
    printf '%s\n' "$out" | tail -4 | sed 's/^/       /'
  fi
else
  note "skipping the dry run until the checks above pass"
fi

# --- summary -----------------------------------------------------------------
printf "\n"
if [ "$fail" -gt 0 ]; then
  printf "${RED}${BOLD}%d check(s) failed${RESET}" "$fail"
  [ "$warn" -gt 0 ] && printf ", ${YELLOW}%d warning(s)${RESET}" "$warn"
  printf ".  Fix the items marked FAIL above, then re-run.\n"
  exit 1
elif [ "$warn" -gt 0 ]; then
  printf "${GREEN}${BOLD}All critical checks passed${RESET} (${YELLOW}%d warning(s)${RESET}).  You are good to go.\n" "$warn"
else
  printf "${GREEN}${BOLD}All checks passed - you are ready for the hackathon.${RESET}\n"
fi
