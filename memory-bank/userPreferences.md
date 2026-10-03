# User Preferences

This file acts as the `USER.md` system described in advanced agentic memory architectures. It stores the specific behavioral, formatting, and workflow preferences of the human user to ensure the agent aligns with their style without needing constant reminders in the prompt.

## Communication Style

- **Drafted messages must read as human-written. Hard rule, not a preference.** Applies to any email, chat
  message, invitation or circulated note the user sends under their own name. Full rule and pre-send
  checklist: `.agents/skills/human-voice-drafting/SKILL.md`. Repository files are exempt.
- *Add preferred tone, verbosity level, etc.*

### Voice calibration — fill from the user's real sent messages, not assumption

- Spelling convention (British / American), and any house terms: *TBD*
- Usual sign-off, and whether they use the recipient's first name: *TBD*
- Emoji and exclamation marks, and with whom: *TBD*
- Length ceiling for a substantial message: *TBD*
- Phrases they genuinely use, so those are preserved rather than sanded off: *TBD*

## Workflow Habits
- Prefer Gemini 3.6 Flash High for bounded routine implementation work.
- Have Gemini return a structured implementation/evidence report; use Codex
  for architectural review, targeted corrections, and final acceptance.
- Gate multi-phase work: implement and review one phase before starting the
  next.

## Formatting Preferences
- *Add specific formatting rules, linting strictness, or code comment styles.*

**Note to Agents**: Update this file when the user explicitly corrects your behavior or requests a persistent change in how you interact with them.
