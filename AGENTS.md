## 🚨 NEW DIRECTIVE (MARCH 2): NON-STOP EXECUTION
- AGENTS MUST WORK ON A TASK NON-STOP UNTIL IT IS FINISHED.
- DO NOT give a response and then stop working.
- DO NOT wait for the user to prompt again if the task is incomplete.

## 🚨 STARTUP MEMORY ENFORCEMENT (NON-SKIPPABLE)
- On **every** gateway startup / context reset, the agent must execute `BOOT.md` (via the bundled `boot-md` hook).
- The agent must read:
  - `AGENTS.md`, `MEMORY.md`, `HEARTBEAT.md`, `SOUL.md`, `TOOLS.md`
  - **ALL** files in `memory/*.md`
- **No user response is allowed until the reads are complete.**
- Use continuous tool calls, background processes, or automated loops to finish the job.