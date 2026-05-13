Title: Integrate Graphify for Knowledge Graph Codebase Context
Problem: Standard grep-based codebase searching is becoming less effective for AI agents navigating large, complex codebases. While our template relies on a highly efficient `memory-bank` system, it does not automatically map the structural dependencies (code, SQL, infrastructure) of the project.
Why now: The user provided a trending tool called Graphify (https://github.com/safishamsi/graphify) which maps any project folder into a queryable knowledge graph. It natively supports all the agent platforms our template targets (Claude Code, Codex, Cursor, Gemini CLI, Antigravity, Copilot). Knowledge graphs represent a significant new trend in LLM context-mapping, shifting from "grepping text" to "querying concepts and relations."
Expected benefit: By giving autonomous agents a `GRAPH_REPORT.md` and a queryable graph, we drastically lower token consumption during autonomous exploration. Agents can navigate the codebase structurally instead of reading raw files to figure out dependencies.
Token/context impact: It may slightly increase startup context if we add `GRAPH_REPORT.md` to the index, but it is expected to significantly reduce token waste and unnecessary file reads during active agent loops.
Affected files: `workflows/build-graph.md` (new), `memory-bank/00-index.md` (to reference the report if it exists), `.gitignore` (to ignore `graphify-out/`).
Implementation outline:
1. Add `graphify-out/` to `.gitignore`.
2. Create a new optional workflow (`workflows/graph-context.md`) instructing users/agents on how to install and use Graphify (`uv tool install graphifyy && graphify .`).
3. Add a section in `docs/agent-skill-ecosystem.md` highlighting Graphify as a recommended third-party context tool.
4. Update `memory-bank/00-index.md` to point to `graphify-out/GRAPH_REPORT.md` (if it exists) for deep structural queries.
Validation plan: Run `graphify .` on the template itself. Evaluate the size of `GRAPH_REPORT.md` and test if an agent like Antigravity can answer architecture questions faster and with fewer tokens using the graph.
Risks/tradeoffs: Graphify adds a Python/uv dependency, which goes against our strict "no external dependencies for the template itself" rule (Section 3 of Improvement Brief). Therefore, it MUST remain an optional integration rather than a mandatory startup step.
Apply now or monitor: Apply Now (as an optional workflow/integration).
