# Model Routing

This file documents how agent tools/models should be selected with minimal overhead.

## Preferred agent tools

| Tool | Use for | Auth/billing |
|---|---|---|
| Cline | Main local coding agent | API key, OpenRouter, or supported provider |
| Codex/OpenAI IDE-style agents | ChatGPT-subscription or API-backed coding tasks where supported | ChatGPT account or API key |
| Google Antigravity | Gemini/agent-first workspace tasks | Google/Antigravity account and supported models |
| Claude-compatible tools | Claude-native coding tasks | Claude-supported auth/API |
| OpenRouter | Multi-model routing | OpenRouter API key |

## Role routing (balanced default)

| Role | Preferred path | Fallback path |
|---|---|---|
| Initialization/planning | Google Antigravity (Gemini) or Codex-style planner | Cline with cost-efficient model |
| Implementation | Cline or Codex/OpenAI IDE-style | OpenRouter-backed coding model |
| Review/refactor | Claude-compatible or Codex-style reviewer | Cline with higher-quality reasoning model |
| Fast utility tasks | Cline with fast/cheap model | Any available low-cost model via OpenRouter |

## Rules

- Do not assume consumer subscriptions can be used inside every third-party extension.
- Prefer official sign-in paths where available.
- Prefer OpenRouter or direct API keys for Cline if subscription OAuth is not supported.
- Use FAST_INIT by default for initialization; escalate to DEEP_AUDIT only when needed.
- Record project-specific model choices here.

## Current defaults

Planning model: TBD  
Coding model: TBD  
Review model: TBD  
Fast/cheap model: TBD  
Long-context model: TBD