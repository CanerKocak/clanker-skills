---
name: simple-english
description: >
  Write technical prose with aircraft-manual clarity. Use for documentation,
  READMEs, procedures, runbooks, error messages, release notes, incident reports,
  and API guides, or when the user requests Simplified Technical English (STE).
  Do not apply this style to marketing or brand copy unless requested.
---

# Simple English

Make technical text easy to act on and difficult to misread. Use the practical
style below by default. Use strict ASD-STE100 checks only when requested.

## Preserve the meaning

Clarity must not change the contract. Preserve these details before editing:

- Facts, actors, conditions, sequence, quantities, units, and time.
- The difference between a requirement, a recommendation, and an option.
- Uncertainty, attribution, evidence limits, and whether a cause is known.
- Code identifiers, commands, paths, API names, and quoted diagnostic text.

Preserve what modal verbs mean in context. In typical technical prose, `must`
states a requirement and `should` states a recommendation. `May` can express
permission or possibility. Do not turn a possible failure into a certain
failure or a suggestion into an instruction. Never add a cause, measurement,
timestamp, or result to make a sentence sound precise.

Use one term for one concept. Keep different concepts distinct: `check`,
`verify`, and `validate` can name different operations in a software system.
Keep established domain terms when a simpler word would change the meaning.
Explain unfamiliar terms when the audience needs the explanation.

## Write like a technical manual

- Use short, complete sentences and common words with precise meanings.
- Give each sentence one main idea. Give each paragraph one topic.
- Use active voice when the actor is known. Do not invent an actor to avoid
  passive voice.
- Start instructions with an action verb. Identify the object of the action.
- Put a condition before the affected instruction: "If the test fails, stop
  the deployment." Keep descriptive sentences in the order that reads best.
- Put prerequisites and necessary warnings before the step they affect.
- Separate actions when the reader must perform them separately. Keep an
  immediate result with its action when that helps the reader verify the step.
- Use lists for steps or parallel information. Use tables for comparisons.
  Do not force a narrative or causal explanation into a table.
- Prefer explicit references when `it`, `this`, or `they` could refer to more
  than one thing.
- Remove filler and repeated meaning. Keep qualifiers that change scope or
  meaning. Use titles that tell the reader what the document is for.

For the default style, aim for at most 20 words in procedural sentences and
25 in descriptive sentences. Split long sentences at a natural boundary.
Preserve meaning and grammatical completeness before meeting a word target.

## Edit and check

Identify the audience and whether the text describes behavior or directs an
action. Preserve its facts and obligations, then rewrite it. Compare the
rewrite with the source for lost conditions, changed authority, invented
facts, and unnecessary words. Do this check privately.

Return the requested text. Add a brief note only when an unresolved ambiguity
or missing fact affects its use. If the user requests a writing audit, show
the relevant source text, the problem, and the proposed replacement. Do not
attach a review transcript or a tally to an ordinary rewrite.

For examples of meaning-preserving edits or strict STE checks, read
[references/manual-english.md](references/manual-english.md). Strict compliance
requires the applicable official rules and dictionary; this skill alone does
not establish compliance.
