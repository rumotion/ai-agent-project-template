# court-skill assessment

Reviewed on 2026-10-31 against the public repository's main branch. This is an
assessment of source and documentation, not a run of its model-driven trial.

[court-skill](https://github.com/alexyc9381/court-skill) by Alex Chen provides a
Claude Code workflow for testing an idea through opposing arguments, rebuttals,
jurors and a final judgment. Its Python helper writes briefs, tracks completion,
counts votes and renders the result under `.court/`. It does not implement
template distribution, GitHub/GitLab upgrades or application preservation.
Sources: [README](https://github.com/alexyc9381/court-skill/blob/main/README.md),
[skill](https://github.com/alexyc9381/court-skill/blob/main/skills/court/SKILL.md),
[helper](https://github.com/alexyc9381/court-skill/blob/main/skills/court/court.py).

## Adoption decision

Use its evidence-oriented opposing-case approach in the existing critic review:
a concrete proposal, a strong failure case, a strong supporting case and explicit
conditions that would change the judgment. Keep deterministic file and test
checks in scripts, while agents handle the reasoning and conflict merges.

Do not install the full jury as an automatic upgrade gate. The documented
default trial uses 17 agent calls and its quick mode uses 11. It targets Claude
Code; this template supports several clients with different tool contracts.
Personas of the same model can share mistakes, so a vote is not a reliability
estimate. These cost and integration judgments are our assessment, not results
of a cross-model benchmark.

No upstream source or prompt text is vendored in this change. The upstream
[MIT license](https://github.com/alexyc9381/court-skill/blob/main/LICENSE)
includes its copyright and permission notice; retain those notices if code or
substantial source material is copied in a later optional integration. Review
the then-current source and costs before installation. No upstream scripts,
agents, plugins or installers were executed for this assessment.

The adopted procedure is in [critic-review](../workflows/critic-review.md).
Remote framework upgrades use the separate
[preservation workflow](../workflows/upgrade-project.md).
