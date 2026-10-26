# Template review: Gemini, Codex, Claude and Antigravity

Verified on October 26, 2026. Inputs: the user-supplied Gemini summary, a local
developer pacing playbook, the template source and the first-party references
below. The complete artifact
`ai_agent_videos_analysis_and_unified_template_proposals.md` was not found in
the repository or at its exact expected Downloads filename. The four videos
and their timestamps were not independently reviewed; their descriptions
remain attributed to the supplied Gemini summary.

## Decisions on the Gemini proposals

| Proposal | Existing template behavior | Decision |
|---|---|---|
| Lean root instructions | AGENTS.md was already under 150 lines; adapters were thin | Remove repetition and leave more startup headroom. Line count alone does not establish token savings. |
| One source of truth and short sessions | Canonical AGENTS, indexed Memory Bank, handoff and context compiler | Keep these mechanisms. Instructions can evolve with evidence; volatile status belongs in separate files. |
| Checks vs plans | Verification commands, falsifiable predictions and contracts already existed | Name an observable acceptance check first. Use short plans for routine tasks and phases for complex work. Do not request approval again for already-authorized implementation. |
| Skills only when useful | Eleven canonical skills with checked mirrors | Do not delete skills based on assumed model competence. Compare errors, quality and cost with and without a skill on the same tasks. |
| Hooks for critical rules | Guard scripts, fixtures and a pre-push backstop | Keep the evidence boundary: synthetic fixtures do not prove every client consumes a denial or provide a sandbox. |
| Autonomous goals | Previously mentioned only in general terms | Document the three current clients and distinguish task continuation from quota accounting. |

The first-100-lines claim needs qualification. Anthropic recommends a table of
contents for **reference files longer than 100 lines**, so partial reads reveal
their structure. This is not a universal tool truncation limit or a requirement
for a Content List in the first 30 lines of every small skill. It also recommends
matching instruction specificity to operation fragility and testing on target
models. [Skill authoring guidance](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).

Structural inspection of the existing entry points found ten of eleven at
100 lines or fewer; `human-voice-drafting` had 163 lines and now has a contents
list. This is structural evidence, not an effectiveness benchmark. The claim
that no skill wins seven times out of nine is not treated as a general result
for this template.

## Client changes affecting compatibility

1. **Antigravity workflows to skills.** Google states that legacy workflow
   directories are no longer indexed for slash commands after October 19,
   2026. Ten thin skill entry points now link to existing canonical workflows;
   generated Claude/Cline mirrors preserve discovery without duplicating
   procedures. This is a structural migration, not a live-client certification.
   [Official migration](https://antigravity.google/docs/migration/workflows-to-skills/).
2. **Goals across three clients.** Codex documents goal lifecycle and budgets;
   Claude Code checks completion between turns; Antigravity continues until
   completion or cancellation. None is the template's cross-provider subscription
   quota meter. [Codex](https://developers.openai.com/cookbook/examples/codex/using_goals_in_codex),
   [Claude](https://code.claude.com/docs/en/goal),
   [Antigravity](https://antigravity.google/docs/commands/goal/).
3. **Client-specific hooks.** Current Antigravity has different native payloads
   from the shipped legacy Gemini CLI example. Codex distinguishes local and
   cloud orchestration hook support. Unverified adapters remain inactive.
   [Antigravity hooks](https://antigravity.google/docs/hooks),
   [Codex hooks](https://learn.chatgpt.com/docs/hooks).
4. **Products are not model IDs.** Removed stale context-window tables,
   marketing names used as model identifiers and universal cache TTL claims.
   Select models by actual client availability, entitlement and project checks.
   Google coding references here mean Gemini/Antigravity. Project Astra is
   described as a universal-assistant project; an Astra/Argonaut coding adapter
   is not invented without an identified client.
   [Project Astra](https://deepmind.google/models/project-astra/).

## Adapting the developer pacing playbook

Implemented one standard-library CLI, `scripts/usage-pacing.py`, with an
on-demand playbook and private SQLite state outside projects. It retains
measured consumption rates, bounded concurrency, completion reserves and short
contexts. Default OFF: the agent explains a concrete plan and warning, then
waits for separate human confirmation. Model switches and handoffs do not
carry pacing authorization into another session.

Claude now documents quota fields in its statusline. The CLI accepts these
numeric fields instead of reading OAuth credentials for an undocumented
endpoint. Codex and Google use manually normalized readings. Missing quota is
not inferred from API prices. [Claude statusline](https://code.claude.com/docs/en/statusline).

Automatic backup pushes, global configuration edits, fixed 150k/250k context
thresholds and API-price-to-subscription conversions were not adopted. Agents
must have useful queued work. The CLI advises; it is not an external spending
controller and cannot stop processes itself. See [usage pacing](usage-pacing.md).

## Local mail and Ponytail

A local mailbox is **not implemented**. The proposed CLI could help independent
processes from different clients, but adds another state layer for a single lead
and its native subagents. Keep it optional. A future implementation needs
read-but-unhandled recovery, total output limits and a tested wake transport.
See [local agent mail assessment](local-agent-mail.md).

Ponytail is a skill/plugin promoting the smallest necessary change after
inspecting the real code. Its published benchmarks do not establish results
on this template. The main principles overlap `karpathy-engineer`; root guidance
now explicitly prefers reuse and configuration while preserving validation,
error handling, security and accessibility. Keep it uninstalled by default.
If repeated overengineering occurs, compare real paired tasks and choose one
instruction layer. [Ponytail upstream](https://github.com/DietrichGebert/ponytail).

## Future verification

Before changing native adapters or releasing, recheck official migration,
skills, hooks, goals and usage documentation. Record installed client versions
and test discovery plus one harmless hook in each required client. Do not
change the template for every model announcement: require a client-contract
change or a reproducible failure. No recurring news monitor or scheduled job
was created by this review.
