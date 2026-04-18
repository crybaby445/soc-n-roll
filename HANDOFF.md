# HANDOFF.md

## Before Exiting This Session

- Commit or stash any uncommitted changes (`git add . && git commit -m "wip: <description>"` or `git stash`)
- Note where you left off below under "Current Work"
- Push to remote if needed (`git push`)

---

## What We Built

A single-file Python CLI tool (`parser.py`) that parses Sysmon XML logs and outputs structured JSON for Event ID 1 (Process Creation) events.

### Files Created

| File | Purpose |
|------|---------|
| `parser.py` | Main parser — XML → JSON with optional filtering |
| `samples/event1.xml` | Sample: `whoami /groups` |
| `samples/event2.xml` | Sample: `cmd.exe` → `powershell.exe` |
| `samples/event3.xml` | Sample: encoded PowerShell cradle from `WINWORD.EXE` |
| `samples/multi_events.xml` | All 3 events in a single `<Events>` wrapper |
| `.claude/settings.json` | Claude Code project permissions config |

---

## How to Use It

```bash
# Parse a single event file
python3 parser.py samples/event1.xml

# Parse multiple events
python3 parser.py samples/multi_events.xml

# Filter by process name
python3 parser.py samples/multi_events.xml --image powershell

# Filter by user (exact match)
python3 parser.py samples/multi_events.xml --user "CONDEF\Administrator"

# Filter by integrity level
python3 parser.py samples/multi_events.xml --integrity high

# Filter by command line (values starting with - need = syntax)
python3 parser.py samples/multi_events.xml --cmdline="-enc"

# Combine filters (AND logic)
python3 parser.py samples/multi_events.xml --image powershell --cmdline="-enc"
```

---

## Decisions Made and Why

| Decision | Rationale |
|----------|-----------|
| Single file, no dependencies | Keeps it portable — runs anywhere Python stdlib is available |
| stdlib `xml.etree.ElementTree` | No pip install needed; sufficient for well-formed Sysmon XML |
| Namespace-aware parsing | Sysmon XML uses `http://schemas.microsoft.com/win/2004/08/events/event` on every element — required for correct field lookup |
| Dual root support (`<Event>` or `<Events>`) | Real exports may wrap multiple events; single-file samples use bare `<Event>` root |
| Filters AND together | More useful for SOC triage — narrow down to specific process + user + integrity combos |
| `--image` / `--cmdline` substring, `--user` exact | Process paths vary; usernames should be precise to avoid false matches |
| Single object vs array output | Mirrors jq conventions — one result is an object, many is an array |
| Exit code `1` on no matches | Allows chaining in shell scripts (`parser.py ... && do_something`) |

---

## What's Left To Do

- [ ] Support other Event IDs (e.g. ID 3 Network Connection, ID 7 Image Load)
- [ ] Add `--output` flag to write JSON to a file instead of stdout
- [ ] Add `--format` flag for CSV or JSONL output
- [ ] Add `--parent-image` filter
- [ ] Handle malformed or missing fields gracefully with a `--strict` mode toggle
- [ ] Add Dockerfile line for `libpython3.12-stdlib` so the devcontainer works out of the box
- [ ] Write unit tests against the sample XML files

---

## Current Work

_Update this section before exiting._

| Item | Status | Notes |
|------|--------|-------|
| `parser.py` + filters | Complete | All 4 filters working and tested |
| Sample XML files | Complete | 3 individual + 1 multi-event |
| CLAUDE.md | Complete | Architecture and usage documented |
