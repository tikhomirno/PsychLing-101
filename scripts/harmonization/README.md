# `scripts/harmonization/`

Shared tooling for keeping the corpus consistent across studies.

**Contributors normally never need anything in here.** To add a dataset, follow the
instructions in the repository [README](../../README.md) — write your own
`preprocess_data.*` and `generate_prompts.*` inside your study folder, as every existing
study does. This directory holds only the few things that must be identical everywhere,
because getting them wrong fails silently.

## Contents

### `bracket_safety.py`

Rules for writing `<<response>>` spans that a training collator can actually find.

Responses are marked with `<<...>>` so that fine-tuning can mask the loss to human
responses only. TRL's `DataCollatorForCompletionOnlyLM` matches the `>>` terminator as a
**token-ID subsequence, not a string**, so whether it is found depends on the character
that follows it. Some combinations tokenize such that the match fails — and it fails
*silently*, with no error and no visible difference in the rendered text.

The consequence is out of all proportion to the cause. One unclosed span does not spoil one
response; the collator does not recover for the rest of that record. A single bad
`<<kathleen?>>` was observed to collapse roughly 200 following items into one unmasked span.

Use `render_response()` for a single response and `join_consecutive()` when one trial
carries several, rather than formatting spans by hand.

> A result worth knowing before you "improve" this: moving trailing punctuation *outside*
> the bracket makes things worse, not better. `>>` followed by `,` breaks the next match
> just as badly as the pattern it was fixing. Relocating a character only moves the danger
> zone. The module is deliberately subtractive and narrow.

## Planned

- `column_map.py` — the canonical map from legacy column names to the unified
  `CODEBOOK.csv` vocabulary, so renames are applied once and identically.
- `regenerate_all.py` — batch runner invoking each study's own two scripts in order, so
  the whole corpus can be rebuilt and diffed with one command.

Neither exists yet; see [HARMONIZATION.md](../../HARMONIZATION.md) for the current status.
