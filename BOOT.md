# BOOT CHECKLIST (NON-SKIPPABLE)

This file is executed at **gateway startup** by the internal hook `boot-md`.

## Prime Directive
**DO NOT respond to the user or take actions until the full memory load is complete.**

## Step 0 — Workspace sanity
- Confirm `workspace.dir` is correct.
- If any required file is missing, create an ALERT message and stop.

## Step 1 — Load core rules (MUST READ)
Read these files in this order:
1. `AGENTS.md`
2. `MEMORY.md`
3. `HEARTBEAT.md`
4. `SOUL.md`
5. `TOOLS.md`

## Step 2 — Load ALL state files (MUST READ ALL)
1) Read `BOOT_FILES.md`
2) Read **EVERY** file listed in `BOOT_FILES.md` (in order).

Notes:
- This includes `memory/*.md` AND all other markdown files that define rules, workflows, products, and system state.
- Do not skip “idea reports”, “marketing”, “skills”, or “automation” docs — they are part of the system state.
- If any file can’t be read (missing/permission), STOP and alert the user.

## Step 3 — Restore mission state
After reading, you must be able to answer:
- What is the CURRENT mission?
- What is DONE?
- What is BLOCKED?
- What is NEXT?

## Step 4 — Persistence requirement
Before ending the session, ensure the conversation is persisted:
- Prefer using OpenClaw’s `session-memory` hook (triggered on `/new` or `/reset`).
- If a restart/disconnect is imminent, trigger a `/reset` (or equivalent) so the session is saved.

## Output requirement (startup)
After finishing Steps 1–3, the first user-visible message (if asked) must start with:

DONE, NOW I KNOW EVERYTHING WHAT WE ARE DOING
