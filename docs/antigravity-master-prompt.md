# Google Antigravity Master Initialization Prompt

Use this prompt after copying the template into a new repository and opening it in Google Antigravity, Cline, Codex/OpenAI-style IDE tooling, or another VS Code-compatible agent environment.

```text
You are operating inside Google Antigravity or a VS Code-compatible IDE with Cline/Codex-style agents available.

Goal:
Initialize this repository as a master AI-agent-ready project using the included template.

Important clarification:
This is not model-weight fine-tuning. This is project-level alignment through canonical instructions, Memory Bank files, workflows, skills, documentation, ignores, and optional MCP configuration.

Critical rule:
AGENTS.md is the single canonical instruction file for all models and tools. GEMINI.md, CLAUDE.md, .clinerules/00-master.md, and .agents/rules/00-master.md are only adapters that point back to AGENTS.md. Do not create conflicting instructions.

Please do the following:

1. Read AGENTS.md completely.
2. Read memory-bank/startup.md.
3. Read memory-bank/00-index.md only to choose additional relevant Memory Bank files.
4. Inspect the repository structure.
5. Identify the actual project type, stack, package manager, runtime, test tools, build commands, deployment assumptions, and any existing source boundaries.
6. Fill in the Memory Bank files with accurate project-specific information:
   - memory-bank/startup.md
   - memory-bank/projectbrief.md
   - memory-bank/productContext.md
   - memory-bank/systemPatterns.md
   - memory-bank/techContext.md
   - memory-bank/activeContext.md
   - memory-bank/progress.md
   - memory-bank/decisions.md
   - memory-bank/risks.md
   - memory-bank/glossary.md
   - memory-bank/model-routing.md
7. Keep unknown items as TBD. Do not invent facts.
8. Review .clineignore and .gitignore. Suggest project-specific exclusions if needed.
9. Review .agents/rules and .agents/hooks.json for Antigravity native execution.
10. Review .agents/skills, .claude/skills, and .cline/skills. Suggest additional skills only if this project needs them.
11. Review workflows/ plus tool-specific workflow mirrors. Suggest project-specific workflows only if useful.
12. Review .vscode/tasks.json and recommended extensions for 1-click developer workflow.
13. For VS Code OpenAI/Codex-style extensions, use the official sign-in or API-key path where supported and treat AGENTS.md as the canonical project instruction file.
14. If ChatGPT Team/Business subscription-backed coding is desired, use official OpenAI/Codex-style IDE sign-in where supported. Do not assume that Cline can directly consume ChatGPT subscription quota; Cline usually uses API keys, direct providers, or OpenRouter.
15. Produce a final initialization report with:
    - Detected stack
    - Filled Memory Bank summary
    - Recommended commands
    - Recommended agent/model setup
    - Recommended skills
    - Recommended workflows
    - Recommended MCP setup, if any
    - Risks and missing information
    - Next best development task

Constraints:
- Do not install dependencies unless asked.
- Do not run destructive commands.
- Do not edit secrets or local-only files.
- Do not make broad architectural changes.
- Keep all Memory Bank files concise.
- Preserve the low-context startup path: AGENTS.md + memory-bank/startup.md by default.
- Update only template files needed for initialization.

After initialization, ask me what first feature, bug fix, automation, documentation task, or branch I want to start.
```

## Recommended model/tool routing

| Need | Recommended path |
|---|---|
| Google/Gemini-native agent workflow | Google Antigravity native agent (`.agents/` workspace rules, skills, MCP, hooks) |
| VS Code agentic IDE coding | Cline / Roo Code / Claude Code with `.vscode/tasks.json` |
| VS Code OpenAI/Codex-style agent | Official OpenAI/Codex extension sign-in or supported API-key flow |
| Terminal agent workflow | Claude Code with `.claude/settings.json` lifecycle hooks |
| Multi-model fallback/routing | OpenRouter in Cline / Roo Code or supported clients |
| Durable project memory | `AGENTS.md` plus `memory-bank/` |
| Reusable expert procedures | `.agents/skills/`, `.claude/skills/`, `.cline/skills/` |
| Repeatable task flows | `workflows/`, `.clinerules/workflows/`, `.agents/workflows/` |
| External live context | Opt-in MCP via the client's native project file (see `.mcp/README.md`) |