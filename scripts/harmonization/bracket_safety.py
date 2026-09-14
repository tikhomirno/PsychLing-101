#!/usr/bin/env python3
"""Rules for writing `<<response>>` spans that a training collator can actually find.

WHY THIS FILE EXISTS
--------------------
Prompts in this corpus mark human responses with `<<...>>`. Fine-tuning setups in
the style of Centaur use TRL's `DataCollatorForCompletionOnlyLM` with
`response_template=" <<"` and `instruction_template=">>"`, which masks the loss so
that each bracketed span becomes its own training target.

The collator matches those templates as **token-ID subsequences, not strings**.
So whether a `>>` is found depends on what character follows it: the tokenizer may
merge `>>` with the next character into a single token that no longer contains the
template's token IDs. When that happens the match fails *silently* -- and it does
not fail for one response only. Once a span fails to close, the collator does not
recover for the remainder of that record: a single bad `<<kathleen?>>` mid-record
was observed to collapse roughly 200 subsequent items into one unmasked span.

That is why this lives in one shared module instead of being re-derived per study:
the failure is invisible in the rendered text, and re-deriving it by intuition
reliably gets it wrong.

WHAT IS ACTUALLY SAFE (verified against the real tokenizer + collator)
---------------------------------------------------------------------
Safe immediately before the closing `>>`:
    ,  !  .  +  ...  `  ??  ???   and ordinary word characters
Safe immediately *after* the closing `>>`:
    .  followed by a newline   <- the convention this corpus uses

Unsafe, and the reason for each rule below:
    `>>` followed directly by `\n`      -- the whole record fails to mask
    `>>` followed directly by `,`       -- breaks the *next* match
    a single trailing `?` before `>>`
    a single trailing `)` before `>>`
    leading/trailing `"` inside the span

A COUNTERINTUITIVE RESULT WORTH KEEPING
---------------------------------------
An earlier version of this fix moved trailing punctuation *outside* the bracket
uniformly. That is wrong, and made things worse: `>>` immediately followed by `,`
breaks the next match just as badly as the pattern it was fixing. Relocating a
character only moves the danger zone. Only the narrow, individually verified set
of patterns below needs to change at all -- everything else must be left alone.

Doubled/tripled `??` and `???` are safe; only a *single* trailing `?` is not.
"""

# Characters that are safe immediately before the closing ">>".
KNOWN_SAFE_BEFORE_CLOSE = (",", "!", ".", "+", "`")

# The terminator every rendered response line should use: a period, then newline.
# Bare ">>\n" (no period) makes the instruction_template match fail for the whole
# record; ">>, " breaks the following match.
SAFE_LINE_TERMINATOR = ".\n"


def sanitize_bracket_response(response: str) -> str | None:
    """Return `response` made safe to embed as ``<<response>>``, or None.

    Purely subtractive: characters are stripped, never relocated or added, for the
    reason given in the module docstring. Returns None when nothing safely
    bracketable remains -- callers must then render the response as plain,
    non-bracketed text (e.g. ``You write "xyz" (not a real word).``) rather than
    emitting an empty ``<<>>``, which is also broken.
    """
    if response in ("-", "/"):
        # No real word content at all.
        return None
    if response.endswith("?") and not response.endswith("??"):
        # A trailing '?' on a one-word answer is a hesitation mark, not part of
        # the word. Doubled '??' is safe and is left alone.
        response = response[:-1]
    if response.endswith(")"):
        # Only a ')' as the very last character breaks the match; a leading '('
        # and internal parens are both fine. Leaving the parens unbalanced is
        # harmless -- tokenization cares only about what is adjacent to '>>'.
        response = response[:-1]
    response = response.strip('"')
    return response or None


def render_response(text: str) -> str:
    """Render one response as a safely terminated, bracketed line.

    Falls back to an explicit non-bracketed statement when the response has no
    safely bracketable content, so the trial stays visible as context without
    being scored as a target.
    """
    safe = sanitize_bracket_response(str(text))
    if safe is None:
        return f'"{text}" (no response recorded){SAFE_LINE_TERMINATOR}'
    return f"<<{safe}>>{SAFE_LINE_TERMINATOR}"


def join_consecutive(segments: list[str]) -> str:
    """Join several bracketed spans that belong to one trial.

    Consecutive spans separated only by ", " (e.g. an association list rendered
    "<<WAR>>, <<FIGHT>>, <<ARMY>>") tokenize such that the ">>" before each comma
    is not found, and the entire run merges into ONE unmasked item per record.
    Separating with ". " keeps identical content and one bracket per response,
    with punctuation the collator can actually locate.
    """
    if not segments:
        return ""
    # Strip each segment's own terminator before joining, then restore exactly one
    # at the end. Without the final period the last span ends "...>>" directly
    # before a newline -- the single worst pattern, which masks the whole record.
    joined = ". ".join(s.rstrip().rstrip(".") for s in segments)
    return joined + "."
