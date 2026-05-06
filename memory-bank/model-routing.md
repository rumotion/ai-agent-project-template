# Model Routing

This file documents how AI models and subscriptions should be used for this project.

## Preferred agent tools

| Tool | Use for | Auth/billing |
|---|---|---|
| Cline | Main local coding agent | API key, OpenRouter, or supported provider |
| Codex/OpenAI IDE-style agents | ChatGPT-subscription or API-backed coding tasks where supported | ChatGPT account or API key |
| Google Antigravity | Gemini/agent-first workspace tasks | Google/Antigravity account and supported models |
| Claude-compatible tools | Claude-native coding tasks | Claude-supported auth/API |
| OpenRouter | Multi-model routing | OpenRouter API key |

## Rules

- Do not assume consumer subscriptions can be used inside every third-party extension.
- Prefer official sign-in paths where available.
- Prefer OpenRouter or direct API keys for Cline if subscription OAuth is not supported.
- Record project-specific model choices here.

## Current defaults

Planning model: TBD  
Coding model: TBD  
Review model: TBD  
Fast/cheap model: TBD  
Long-context model: TBD