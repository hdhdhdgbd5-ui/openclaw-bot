# WORKFLOW_AUTO.md — Empire Continuity Protocol (Non-Skippable)

## Goal
Make OpenClaw **never forget** where it stopped after any gateway restart, model switch, compaction, `/new`, or `/reset`.

## Enforcement Mechanism
- **BOOT.md** is executed on gateway startup by the bundled internal hook **`boot-md`**.
- `BOOT.md` requires reading:
  - `AGENTS.md`, `MEMORY.md`, `HEARTBEAT.md`, `SOUL.md`, `TOOLS.md`
  - **ALL** `memory/*.md`
- The agent must not respond until the reads are complete.

## Session persistence
- Bundled internal hook: **`session-memory`**
  - Saves the prior session context to `memory/YYYY-MM-DD-<slug>.md`
  - Triggered when `/new` or `/reset` is issued.

## Operational Rules
1. After any restart/compaction: **Read everything first.**
2. No “what next?” questions: the system must infer next steps from memory.
3. If a restart is likely, **force a save** (issue `/reset`) so `session-memory` writes the transcript.

## Current known limitation
- `session-memory` only triggers on `/new` or `/reset` (not on crashes/power loss).
- Mitigation: proactively trigger `/reset` on planned restarts.
