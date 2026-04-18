# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> When resuming work on this project, read `HANDOFF.md` first — it captures what was built, decisions made, and what's left to do.

## Environment

This repo runs inside a Dev Container (Ubuntu 24.04 + Node.js). On devcontainer start, the `.ona/automations.yaml` automation installs Claude CLI globally via `npm install -g @anthropic-ai/claude-code`.

The Dockerfile at `.devcontainer/Dockerfile` is available for adding system-level dependencies.

`libpython3.12-stdlib` must be installed for `parser.py` to run — only `python3-minimal` ships in the devcontainer by default. Add to `.devcontainer/Dockerfile`:

```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends libpython3.12-stdlib
```

## Running the Parser

```bash
python3 parser.py <path-to-xml>
```

**Filtering flags** (all optional, ANDed together):

```bash
--image TEXT       # Image path contains value (case-insensitive substring)
--user TEXT        # User exact match (case-insensitive)
--integrity LEVEL  # IntegrityLevel: high, medium, low, or system
--cmdline TEXT     # CommandLine contains value (case-insensitive substring)
```

Values starting with `-` require `=` syntax: `--cmdline="-enc"`

## Project: Sysmon XML Parser

A Python tool that parses Sysmon XML logs and extracts key fields from **Event ID 1 (Process Creation)** events.

### Fields Extracted

| Field | Description |
|-------|-------------|
| `EventID` | Always `1` for Process Creation |
| `UtcTime` | Event timestamp |
| `Image` | Full path of the spawned process |
| `CommandLine` | Full command line used |
| `User` | Account that ran the process |
| `IntegrityLevel` | Process integrity level |
| `ParentImage` | Full path of the parent process |
| `ParentCommandLine` | Parent process command line |
| `Computer` | Hostname where the event occurred |
| `Hashes` | Hash(es) of the process image |

### Architecture

- **Single file** (`parser.py`) — no external dependencies, stdlib only (`xml.etree.ElementTree`, `argparse`, `json`)
- **Namespace-aware XML parsing** — all elements use the Sysmon namespace `http://schemas.microsoft.com/win/2004/08/events/event`
- **Dual root support** — handles both a bare `<Event>` root and a wrapper element (e.g. `<Events>`) containing multiple `<Event>` children
- **Filter logic** — `matches_filters()` ANDs all active filters; unset filters are skipped
- **Output shape** — single event → JSON object; multiple events → JSON array
- **Exit codes** — `1` on file-not-found, parse error, no Event ID 1 records, or no events matching filters

### Samples

| File | Description |
|------|-------------|
| `samples/event1.xml` | `whoami /groups` execution |
| `samples/event2.xml` | `cmd.exe` spawning `powershell.exe` |
| `samples/event3.xml` | Encoded PowerShell cradle spawned from `WINWORD.EXE` |
| `samples/multi_events.xml` | All 3 events in a single `<Events>` wrapper |
