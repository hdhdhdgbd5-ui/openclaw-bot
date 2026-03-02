## 🚨 NEW DIRECTIVE (MARCH 2): NON-STOP EXECUTION
- AGENTS MUST WORK ON A TASK NON-STOP UNTIL IT IS FINISHED.
- DO NOT give a response and then stop working.
- DO NOT wait for the user to prompt again if the task is incomplete.

## 🚨 ABSOLUTE MEMORY ENFORCEMENT (NON-SKIPPABLE)
- On every gateway startup / context reset, the agent must execute `BOOT.md`.
- `BOOT.md` requires reading `BOOT_FILES.md` and then **every file listed** inside it before responding.
- If any file is missing/unreadable: STOP and alert Tez. Do not proceed.
