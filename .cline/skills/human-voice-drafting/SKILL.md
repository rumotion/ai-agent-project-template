---
name: human-voice-drafting
description: Hard rules for drafting any email, chat message, meeting note or comment the user will send under their own name. Use whenever the user asks for a message to a colleague, client, counsel, vendor or team. The output must read as written by a person, with none of the stylistic tells that identify assistant-generated text. A recipient identifying a draft as AI-written is a work-relationship failure, not a style preference.
---

# Human Voice Drafting

## Why this rule exists

This skill was codified after a real incident. A user sent an email drafted by an assistant to a senior
colleague. A third party read it and told the user it "screams AI written". The flagged sentence was the
opening:

> *"That's on me — I sent you five things I was worried about and never said what I wanted you to do with
> them. Let me try again."*

The email was substantively good. It was accurate, well organised, and it said the right things. **It still
damaged the user's standing**, because a reader who decides a message was machine-written stops reading it
as the sender's own thinking and starts reading it as something the sender did not bother to write. That
judgement is not recoverable within the same thread, and it is not repaired by the quality of the content.

This applies to every word that leaves the project under the user's name.

## The hard rule

**Anything the user will send under their own name must be written so that no recipient would suspect it
was drafted by an AI.** This outranks completeness, structure and polish. A shorter, plainer message that
reads as human is always the correct trade against a thorough one that does not.

If a construction below is needed to say something important, say it another way. Do not keep the
construction and hope it passes.

## Banned constructions

These are the tells. None of them may appear in a draft.

### 1. The confessional opener and self-narration

Never open by narrating your own failure, apologising in a balanced clause, or announcing a retry. Never
describe the message inside the message.

- ❌ "That's on me — I sent you five things and never said what I wanted. Let me try again."
- ❌ "Let me be clearer about what I'm asking."
- ❌ "I realise I wasn't specific enough in my last message."
- ✅ "Sorry, my last email wasn't clear about what I needed."

One short apology, then the point. A person writes six words of regret, not a sentence diagram of it.

### 2. Em-dashes doing dramatic work

The em-dash pivot is the single loudest tell. Use a comma, a full stop, or brackets.

- ❌ "That answer is wrong — and they will find it."
- ✅ "That answer is wrong, and they will find it."

More than one em-dash in a message is disqualifying on its own. Zero is the target in email.

### 3. The tricolon summary

Never recap what you just said in a tidy rhythm of three.

- ❌ "So: two need a decision from you, one needs a document check, and two just need a yes."
- ✅ Delete it. The reader has just read the list.

Any sentence starting "So:", "In short," or "To summarise," that restates the message is cut.

### 4. Mid-sentence bold for emphasis

Bold belongs in a document, not in a message to a colleague. Never bold a clause inside a running sentence.

- ❌ "What I'm asking for is one thing: **read the draft and tell me if it's fine to send.**"
- ✅ "What I need is for you to read the draft and tell me if it's OK to send."

### 5. Labelled paragraph openers

No pseudo-headers inside prose.

- ❌ "Context:" / "The ask:" / "Bottom line:" / "Why I'm raising it at all:"
- ✅ Start the paragraph with the sentence itself.

### 6. Performed humility and inserted personality

Deference written as a catchphrase reads as a costume, especially more than once in a message.

- ❌ "Your call, not mine." / "above my pay grade" / "I'm just the technical guy here"
- ✅ "I don't know the answer to that one." / "You can see the contract and I can't."

Say the deference. Do not perform it.

### 7. Repeated rhetorical frames

If a construction appears twice in one message, rewrite one of them. Watch for "I'd rather X than Y",
"It's not A, it's B", "not only… but also", and rule-of-three lists that were not naturally three.

### 8. Assistant vocabulary

Do not use, in any message: *delve, leverage* (as a verb), *robust, holistic, seamless, streamline,
utilise, myriad, navigate* (figurative), *landscape* (figurative), *crucial, pivotal, testament to, it's
worth noting, it's important to note, that said, moreover, furthermore, underscore* (figurative),
*tapestry, journey* (figurative), *ensure* where "make sure" works.

### 9. Emoji and exclamation marks

Only where the user has used them with that recipient. Default is none.

### 10. Uniform paragraph rhythm

Assistant text has evenly-sized paragraphs and even sentence lengths. Human messages do not. Let one
paragraph be a single line. Let one sentence run long and the next be four words. This breaks the tell more
effectively than any individual word choice.

## Positive shape

- **Short.** If it needs to be long, the length is in the substance, not the framing.
- **Straight into the point.** The first line says what is wanted or what happened.
- **Contractions throughout.** "I haven't", "won't", "don't", "it's".
- **Specific rather than balanced.** A person names the one thing that worries them. An assistant lists the
  considerations on both sides.
- **Ends flat.** A sign-off. No summary, no restatement of the ask, no motivational close.

## Calibrate to this project's user

Fill these in per project, from the user's real sent messages rather than assumption. Record answers in
`memory-bank/userPreferences.md` under Communication Style.

- Spelling convention (British / American) and any house terms.
- Usual sign-off, and whether they use the recipient's first name.
- Whether they use emoji, and with whom.
- Typical length ceiling for a substantial message.
- Any phrases they genuinely use, so those are preserved rather than sanded off.

If no samples exist, say so and default to plain, short and unadorned.

## Before handing over any draft

Run this list. Do not skip it because the draft "reads fine" — the failed email read fine too.

1. Count em-dashes. More than one, rewrite.
2. Find every bolded run inside a sentence. Remove it.
3. Read the first two sentences alone. Would a busy person write exactly that? If they narrate the message
   itself rather than its subject, rewrite.
4. Find the closing paragraph. If it summarises, delete it.
5. Search for every word in the banned vocabulary list.
6. Check for any construction used twice.
7. Read it aloud in the user's voice. Anything that sounds performed comes out.
8. State the word count when handing it over.

## Scope and limits

- **Applies to:** email, chat (Slack/Teams), calendar invitations, meeting notes circulated to others,
  comments on a shared document, pull request descriptions written for humans, and anything else drafted
  for the user to send or post.
- **Does not apply to:** repository analysis files, registers, memory-bank entries, commit messages, or
  anything whose reader is the project record rather than a person. Those may stay structured.
- **Never overrides accuracy.** If plain phrasing would make a claim less true, keep the true version and
  find different plain words. Do not soften a fact to make a sentence flow.
- **Never rewrite a sent message.** Once it has gone it is a record. Fix the next one.
- **Never transmit.** This skill drafts. Sending is the user's action, always.

## Worked example

See `reference-worked-example.md` in this directory for a before-and-after with the tells annotated line by
line.
