# Template Improvement Brief

Use this file as a handoff brief for another LLM, reviewer, or future maintainer. The goal is to explain what this template is trying to achieve, what exists today, what problems remain, and how to evaluate future improvements as the agent tooling market changes.

## 1. Mission

This repository is an AI-agent project starter template.

Its mission is to provide a clean, copyable, low-context starting point for software projects developed with multiple agent tools, including:

- Cline
- Google Antigravity / Gemini
- Codex / ChatGPT-style coding agents
- Claude-compatible tools
- OpenRouter-backed models
- VS Code-compatible AI tooling

The template should help users start new projects quickly while preserving context for the actual product work instead of spending excessive tokens on template instructions.

## 2. Main goals

1. Keep startup context small.
2. Keep `AGENTS.md` as the canonical instruction file.
3. Support multiple agent tools without duplicating conflicting rules.
4. Use a concise Memory Bank for durable project context.
5. Make first-time initialization beginner-friendly.
6. Avoid secrets, generated artifacts, and project-specific stack assumptions.
7. Stay easy to improve as agent tooling evolves.

## 3. Non-goals

- Do not become a full application framework.
- Do not force one provider, model, IDE, or agent tool.
- Do not include real API keys, OAuth tokens, credentials, or production secrets.
- Do not add dependencies unless they are necessary for template functionality.
- Do not make every agent read all docs, workflows, skills, scripts, and Memory Bank files by default.

## 4. Current architecture

### Canonical instructions

- `AGENTS.md` is the source of truth for all agents.
- `GEMINI.md`, `CLAUDE.md`, `.clinerules/`, and `.agents/` should remain thin adapters that point back to `AGENTS.md`.

### Memory Bank

- `memory-bank/startup.md`: tiny current snapshot for every task.
- `memory-bank/00-index.md`: routing map for deciding what to read next.
- Other Memory Bank files are lazy-loaded only when relevant.

### Initialization modes

`AGENTS.md` defines two explicit modes:

- `FAST_INIT` (default): low-token initialization with strict read/update boundaries.
- `DEEP_AUDIT` (explicit only): deeper review for publishing, architecture audits, or broad cleanup.

### Scripts

- `python scripts/init-fast.py`
  - Runs lightweight validation.
  - Prints a short prompt for a new agent context window.
- `python scripts/check-template.py --fast`
  - Lightweight startup/integration validation.
- `python scripts/check-template.py`
  - Full validation for publishing/readiness checks.

### Workflows

- `workflows/init-lite.md`: short FAST_INIT procedure.
- Other workflows cover planning, implementation, debugging, refactoring, and Memory Bank updates.

## 5. Recommended new-user flow

For a freshly cloned/copied template:

```bash
python scripts/init-fast.py
```

Then paste the printed prompt into a new agent context window:

```text
FAST_INIT + TOKEN_SAVER.
Follow AGENTS.md initialization modes exactly.
Use minimal turns and minimal narration.
Update only allowed Memory Bank files.
Keep unknowns as TBD.
Ask only critical questions before any escalation.
Return a short final summary.
```

Use full validation before publishing or deep review:

```bash
python scripts/check-template.py
```

## 6. Known token/context problem

The template now keeps the project-file FAST_INIT read set small, but full autonomous agent sessions can still consume many tokens.

Observed examples from Cline + Codex autonomous ACT mode:

- Initial broad initialization: about 87.6k tokens.
- After FAST_INIT improvements: about 55k tokens.
- After TOKEN_SAVER prompt: about 37k tokens.

Measured template content for the FAST_INIT baseline was much smaller:

- `AGENTS.md`: about 3.4k characters
- `memory-bank/startup.md`: about 0.4k characters
- `memory-bank/00-index.md`: about 0.8k characters
- `README.md`: about 4.9k characters
- Total: about 9.5k characters, roughly 2.4k-2.6k input tokens before platform/tool overhead.

Conclusion: remaining high token usage is mostly from agent runtime overhead, such as system prompts, tool schemas, autonomous tool loops, status updates, and completion summaries.

## 7. Improvement principles

Future improvements should follow these principles:

1. Preserve multi-agent compatibility.
2. Keep `AGENTS.md` canonical and compact.
3. Prefer lazy loading over eager reading.
4. Prefer deterministic local scripts over complex setup.
5. Keep beginner workflow simple.
6. Keep Memory Bank concise and operational.
7. Keep public-template safety strong.
8. Measure token usage before and after changes.

## 8. Improvement backlog

Consider these possible future improvements:

### Token/context optimization

- Add a stricter FAST_INIT turn budget recommendation.
- Add a short “minimal completion format” to `AGENTS.md`.
- Add a token benchmark script that estimates startup file size and prints expected token ranges.
- Explore whether some optional agent packs should move out of active root paths.
- Test whether specific IDE/agent settings reduce autonomous narration overhead.

### Documentation clarity

- Keep all beginner docs aligned around `python scripts/init-fast.py`.
- Keep advanced/deep-audit guidance clearly separate from daily startup.
- Periodically search docs for outdated startup prompts.

### Validation

- Add optional checks ensuring README/docs mention both `init-fast.py` and `check-template.py --fast`.
- Add `--json` output to validation scripts for automated tooling.
- Add a benchmark mode that reports startup-path character counts.

### Memory Bank hygiene

- Keep template Memory Bank files generic.
- Avoid recording one-off local run traces in publishable template state.
- Add a small script or checklist to detect run-specific phrases before publishing.

### Agent ecosystem updates

- Revisit support for new agent standards, MCP practices, IDE integrations, and provider auth flows.
- Review whether adapter files are still needed as tools evolve.
- Watch for improvements in Cline, Antigravity, Codex/OpenAI, Claude Code, Gemini, OpenRouter, and VS Code agent behavior.

## 9. Market / industry scan checklist for another LLM

When asking another LLM to review this template, ask it to check:

1. Are there newer best practices for `AGENTS.md`-based repo instructions?
2. Are Cline/Claude Code/Codex/Gemini/Antigravity startup conventions changing?
3. Are there better ways to reduce autonomous agent orchestration overhead?
4. Are there safer or clearer patterns for Memory Bank-style persistent context?
5. Are MCP config conventions changing?
6. Are there new provider-routing or model-routing patterns worth adopting?
7. Are docs too long for beginners?
8. Are validation scripts still sufficient for public-template safety?
9. Are any files likely to cause agents to over-read by default?
10. Can the template be simplified without losing robustness?

## 10. Suggested prompt for external LLM review

Use this prompt with another LLM:

```text
You are reviewing an AI-agent project starter template.

Read this file first: docs/template-improvement-brief.md
Then inspect only the files needed to answer:

1. Is the template aligned with current best practices for Cline, Claude Code, Codex/ChatGPT-style agents, Gemini/Antigravity, OpenRouter, and VS Code agent workflows?
2. Are there newer industry patterns that can reduce context/token usage further?
3. Are the docs and first-run flow simple enough for beginners?
4. Are there safety or maintainability issues before publishing as a public GitHub template?

Return:
- top 5 recommended improvements
- risks/tradeoffs
- files likely to change
- whether each recommendation is low/medium/high effort
- whether it should be applied now or monitored for later

Do not propose adding dependencies unless clearly justified.
Do not recommend broad rewrites unless the benefits are substantial.
```

## 11. Proposal format for future improvements

Future improvement proposals should include:

```text
Title:
Problem:
Why now:
Expected benefit:
Token/context impact:
Affected files:
Implementation outline:
Validation plan:
Risks/tradeoffs:
Apply now or monitor:
```

## 12. Success metrics

Track these metrics over time:

- FAST_INIT file-read character count.
- FAST_INIT observed token usage in Cline autonomous mode.
- FAST_INIT observed token usage in Claude Code.
- FAST_INIT observed token usage in Codex/OpenAI-style tools.
- Number of files read during initialization.
- Number of tool calls during initialization.
- User steps required from fresh clone to initialized Memory Bank.
- Full validation pass/fail status.

## 13. Maintenance cadence

Review this file when:

- Agent tools release major changes.
- Startup token usage increases unexpectedly.
- New provider/model routing options become available.
- The template adds/removes major files or workflows.
- Users report confusion in first-run setup.

Recommended routine:

1. Run `python scripts/init-fast.py` in a fresh clone/context.
2. Record observed token usage and files read.
3. Run `python scripts/check-template.py --fast`.
4. Run `python scripts/check-template.py` before publishing.
5. Update this brief when decisions or goals change.

## 14. Current status

Current status: template is optimized for low-context startup but still subject to fixed overhead from autonomous agent runtimes.

The most important next improvement area is not more documentation; it is measuring and reducing autonomous-agent turn count and verbosity without weakening reliability.
