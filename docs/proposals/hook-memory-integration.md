Title: Hook-based Memory and Dream Phase Consolidation
Problem: Our current `memory-bank` is highly effective across models, but it relies on the active agent (or user) to manually update files. This costs valuable context tokens and distracts the agent from its primary coding task. Furthermore, agent-driven logging is inconsistent—sometimes they forget to update `handoff.md` or `progress.md`.
Why now: A recent architectural pattern (referenced from Tomas Bratanic's work on Unified Agentic Memory) uses IDE/harness **lifecycle hooks** (`SessionStart`, `UserPromptSubmit`, `PostToolUse`) to passively log all events outside of the LLM context.
Expected benefit: 
1. **Zero-token logging**: We can log agent actions without costing tokens.
2. **Dream Phase**: We can run a background batch script (a "Dream Phase") that reads the passive logs and updates our markdown memory bank files offline, separating "doing" from "remembering."
Token/context impact: Reduces active context overhead to near zero for memory management.
Affected files: Future introduction of a `hooks/` directory, updates to `AGENTS.md` to explain offline memory consolidation.
Implementation outline:
1. Research cross-IDE hook support (Cursor, Claude Code, Cline all support different hook standards).
2. Create lightweight shell scripts in a `scripts/hooks/` directory to log events to a local `.agent-logs/` folder (instead of requiring Neo4j).
3. Provide a `python scripts/dream.py` script that users can run to summarize `.agent-logs/` into the `memory-bank/` files.
Validation plan: Test if Cline and Claude Code hooks fire consistently. Evaluate if the `dream.py` script accurately captures progress without agent intervention.
Risks/tradeoffs: High fragmentation across IDEs. Cursor hooks differ from Claude Code hooks. Maintaining cross-harness hooks adds complexity to the template. 
Apply now or monitor: **Monitor**. The concept of a "Dream Phase" is brilliant, but standardizing hooks across 7 different AI tools is too fragile for our zero-dependency core right now. We will track IDE hook standardization.
