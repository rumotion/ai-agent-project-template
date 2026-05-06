# Architecture

Describe the system architecture here after the template is initialized for a real project.

For AI-operational context, keep concise architecture facts in `memory-bank/systemPatterns.md` and link here for deeper detail.

## File organization convention

Use `docs/file-organization.md` as the detailed guide.

- `references/`: source/reference material for people and agents; not shipped by default.
- `assets/`: source project assets and content inputs that may become part of the app or website.
- `public/`: stack-specific static runtime files, created only when the chosen app framework uses it.
- `src/assets/`: stack-specific imported runtime assets, created only when the chosen source stack uses it.
- `docs/`: human-readable project documentation.
- `memory-bank/`: concise durable project context for agents.

When a project chooses a stack, document any project-specific folder decisions here.