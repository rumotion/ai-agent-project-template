# Public release review: v1.0.0

## Post-release main update — 2026-10-26

Scope: the current-client/workflow and optional pacing update described in
`CHANGELOG.md` under Unreleased. No new tag or GitHub Release is created.

- Compare against fetched public main and inspect every outgoing text blob,
  the complete current tracked file inventory and new commit metadata.
- Check known credential/private-key patterns, secret-like assignments,
  personal email/home paths, local file URIs and sensitive runtime filenames.
  Review binary additions explicitly; none are intended in this update.
- Keep unpublished commits with non-no-reply author metadata on a local-only
  archive branch. Construct the public update on the existing public parent
  with GitHub no-reply metadata; do not rewrite published history.
- Publish only the reviewed main ref, never all branches or tags. Preserve the
  local pre-push block after the explicitly authorized publication command.
- Ignore-state review excludes runtime logs, scratch, historical local proposals,
  caches, pacing databases and the developer's original local playbook.
- Run full local validation before publication. Native client integration and
  provider quota/cache measurements remain unverified.

The company workflow project is created separately after publication. Its
project-specific context is local-only and never enters this public template.
Pattern scans cannot prove the absence of every possible confidential fact;
the reviewed scope and actual Git transmission inputs are the boundary here.

### Main update receipt

- Published source commit: `5f46a6610122ef8c5b9a00e1ac9e18b735a47a56`.
- [Hosted validation run 40409209097](https://github.com/rumotion/ai-agent-project-template/actions/runs/40409209097)
  passed all four Windows/Linux and Python 3.9/current jobs.
- Reviewed 291 tracked files and 39 outgoing text blobs, plus the sole outgoing
  commit's author/committer metadata. No checked sensitive-pattern matches or
  non-English documentation remained. These counts describe that source push.
- Verified the remote main SHA after push and preserved the installed local
  pre-push hook byte-for-byte. No archive branches, tags or company content
  were included. The follow-up fixes generated starter text separators and
  records this receipt; it undergoes a separate outgoing review.

## Original release review

Scope: rumotion/ai-agent-project-template, the reviewed public main snapshot and
its annotated v1.0.0 tag. Private workspace files are not release inputs.

## File and history checks

- Reviewed current tracked content and 563 historical UTF-8 text blobs using
  private-key, credential-token, assignment, email and local-path patterns.
- No credential/private-key matches were found. One historical function parameter
  was a scanner false positive. Historical absolute file links were already in
  published history; no attempt is made to erase or rewrite that public history.
- No tracked environment credentials, private-key files, runtime logs, media,
  database files or binary assets were found in the scanned history.
- Hardcoded local-project examples in skills/workflows were replaced with relative
  paths; generated mirrors were refreshed before creating the public snapshot.
- Unpublished Memory Bank notes about unrelated projects were removed from the
  public tree and excluded from release ancestry. Original work remains local.
- The release snapshot's parent is existing public main. Only the reviewed main
  and specific tag are published, not local backup branches or all references.
- New release commits/tags use the GitHub account's no-reply address. Existing
  published commit metadata is preserved; unpublished contacts are not added.
- `.gitignore` and the actual index/file inventory were checked independently.
  Ignored logs, caches, local notes and scratch remain outside Git transmission.

## Verification and limits

The dependency-free template gate and the targeted context, contract, hook and
mirror regressions run before publishing. GitHub's Windows/Linux and Python
3.9/current matrix provides the hosted runtime check. The landing page describes
advisory controls honestly; there is no sandbox or provider-cache guarantee.

Pattern scanning is evidence of the checks performed, not proof that every
possible confidential fact or encoded credential can be recognized. Future
release changes need another outgoing-content review. Keep private project
memory in its own local repository and never merge it into this public template.

## Publication receipt

- Release: [v1.0.0](https://github.com/rumotion/ai-agent-project-template/releases/tag/v1.0.0).
- Reviewed release commit: `ae5b1ad31d4a5f6bf9d89b624cfd3e19f65d360a`.
- Hosted validation: [run 37156383241](https://github.com/rumotion/ai-agent-project-template/actions/runs/37156383241).
  All four Windows/Linux and Python 3.9/current jobs passed.
- GitHub secret scanning and push protection are enabled. No open secret alerts
  were returned when the repository was checked during publication.
- Only main and the annotated v1.0.0 tag were pushed; local backup branches were
  excluded. The installed local-only hook was verified unchanged after the push.
- The existing CI workflow invokes the expanded full validator, including all
  new regressions. It was retained without requesting workflow-edit privileges.
