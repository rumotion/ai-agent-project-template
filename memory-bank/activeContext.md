# Active Context

## v1.0.0 release preparation - 2026-10-03

- Updated README, native SVG hero, release notes and changelog to match current behavior.
- Public Memory Bank contains template facts only. Unrelated project notes and
  unpublished operational history are excluded from the public release ancestry.
- Preserved implementation history locally; the release snapshot advances existing
  public main without rewriting published commits. New metadata uses GitHub no-reply.
- Pattern review covers tracked files, historical blobs, outgoing objects and
  author metadata. Ignored logs, caches and local scratch are not release inputs.
- Local regression checks are required before push; remote CI is checked afterward.
- Native containment, live client denials and provider cache savings remain unverified.

## Refuted hypotheses

- Worker-writable hooks were not a universal publishing boundary. They prevent
  ordinary accidents; external supervisor controls are not supplied.
- Comparing durable prefixes across clients ignored client-specific notes. Tests
  now compare status changes within each renderer.
