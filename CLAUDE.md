# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment

This repo runs inside a Dev Container (Ubuntu 24.04 + Node.js). On devcontainer start, the `.ona/automations.yaml` automation installs Claude CLI globally via `npm install -g @anthropic-ai/claude-code`.

The Dockerfile at `.devcontainer/Dockerfile` is available for adding system-level dependencies.

## Repository State

This is a greenfield repository. No application code exists yet. When code is added, update this file with build, lint, and test commands.

## Project: Sysmon XML Parser

A Python tool that parses Sysmon XML logs and extracts key fields from **Event ID 1 (Process Creation)** events.

### Fields to Extract

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

### Output Format

JSON — one object per event. Multiple events produce a JSON array.
