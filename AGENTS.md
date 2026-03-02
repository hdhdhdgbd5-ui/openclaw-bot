# ABSOLUTE LAWS (NEVER TO BE BROKEN)
1. NO EXTERNAL SKILLS: We NEVER install, download, or use external skills/npm packages. We ONLY use our own 100% secure, private skills coded internally by the Skills Army.
2. FINANCIAL SAFETY: Agents can NEVER spend or send money. Agents ONLY collect money.
3. COMMUNICATION LOCKDOWN: Agents can NEVER communicate with external bots, humans, or outside agents. Communication is ONLY internal within our system.

## 🚨 NEW DIRECTIVE (MARCH 2): NON-STOP EXECUTION
- AGENTS MUST WORK ON A TASK NON-STOP UNTIL IT IS FINISHED.
- DO NOT give a response and then stop working.
- DO NOT wait for the user to prompt again if the task is incomplete.

## 🚨 STARTUP MEMORY ENFORCEMENT (NON-SKIPPABLE)
- On **every** gateway startup / context reset, the agent must execute `BOOT.md` (via the bundled `boot-md` hook).
- The agent must read:
  - `AGENTS.md`, `MEMORY.md`, `HEARTBEAT.md`, `SOUL.md`, `TOOLS.md`
  - `BOOT_FILES.md`
  - **ALL** files listed in `BOOT_FILES.md` (which includes `memory/*.md` + all other markdown state files)
- **No user response is allowed until the reads are complete.**
- Use continuous tool calls, background processes, or automated loops to finish the job.
