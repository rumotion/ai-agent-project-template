# Security Policy

## Secrets

Do not commit secrets, tokens, OAuth credentials, private certificates, production configuration, or `.env` files.

Use `.env.example` to document required variables without values.

Before publishing a repository created from this template, run:

```bash
python scripts/check-template.py
```

The validator flags common public-template hygiene issues without printing secret values.

Do not copy a previous project's `.git/` directory into a new public starter unless you intentionally want to preserve its commit history and remote URLs.

## Agent safety

Agents must not modify secrets, production credentials, deployment credentials, or customer data unless explicitly instructed and reviewed.

## Reporting issues

Record security-sensitive risks in `memory-bank/risks.md` and handle them with a careful plan before implementation.