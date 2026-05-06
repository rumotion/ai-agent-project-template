# File Organization

Use this guide when adding project inputs, references, assets, and content files to a project created from this template.

## Quick rule

- Put **reference-only material** in `references/`.
- Put **source assets for the project** in `assets/`.
- Put **files served by an app or website** in the stack's runtime folder, usually `public/` or `src/assets/`, after that stack exists.
- Put **durable project understanding** in `memory-bank/`.
- Put **human-facing documentation** in `docs/`.
- Do not commit secrets, private client files, licensed material, or very large binaries unless intentionally approved.

## Folder map

| File type | Put it here | Use for | Commit by default? |
|---|---|---|---|
| PDFs for research, briefs, specs, transcripts | `references/docs/` | Human/agent reference only | Yes, if public-safe and reasonably small |
| Text/Markdown notes used as raw reference | `references/docs/` | Source/reference material | Yes, if public-safe |
| Reference images, screenshots, mood boards | `references/media/` | Inspiration or analysis, not shipped | Yes, if public-safe and reasonably small |
| Original/editable project images | `assets/images/` | Source assets to process or copy into the app | Yes, if licensed/public-safe |
| JSON/CSV seed data or content | `assets/data/` | Project content/data inputs | Yes, if public-safe |
| Static website files served directly | `public/` | Runtime files copied as-is by many web frameworks | Only after a web stack is chosen |
| Imported frontend assets | `src/assets/` | Assets imported by app source code | Only after a source stack is chosen |
| Architecture/setup/API docs | `docs/` | Human-readable project documentation | Yes |
| Project facts/decisions/current context | `memory-bank/` | Concise durable agent context | Yes, but keep concise |
| Generated outputs, exports, cache files | `generated/`, `dist/`, `build/`, `tmp/` | Build/runtime artifacts | Usually no |
| Secrets, API keys, credentials, tokens | Local `.env`, OS keychain, IDE settings | Local/private configuration | Never |

## Reference files vs project files

Reference files help people and agents understand the project but are not part of the shipped product.

Examples:

```text
references/docs/client-brief.pdf
references/docs/research-notes.md
references/media/inspiration-homepage.png
references/media/logo-reference.jpg
```

Project files are intended to become part of the app, website, content system, or build process.

Examples:

```text
assets/images/hero-source.png
assets/data/projects.json
public/favicon.svg
public/images/hero.webp
src/assets/logo.svg
```

## Web project guidance

For a typical website or app:

1. Keep original/reference material in `references/`.
2. Keep source content/assets in `assets/`.
3. After choosing a stack, move optimized runtime files into the stack's convention:
   - Vite/React: usually `public/` for direct static files or `src/assets/` for imported assets.
   - Next.js: usually `public/` for direct static files.
4. Document any project-specific convention in `docs/architecture.md` and `memory-bank/systemPatterns.md`.

## Safety and size rules

- Do not commit private/client/confidential material unless the repository is private and the user approves.
- Do not commit copyrighted or licensed assets unless redistribution is allowed.
- Do not commit real `.env` files, credentials, tokens, or provider keys.
- Avoid committing very large media or design files to the base template. The default `.gitignore` blocks common large formats; copied projects can intentionally relax those rules if needed.
- If an agent should use a resource as context, tell it exactly which file or folder to inspect.
