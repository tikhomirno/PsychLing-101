# Harmonization

This branch (`corpus-fixed`) is a corrected, ready-to-use version of the PsychLing-101
corpus. The contributor submissions exactly as they were merged remain on `main`; nothing
here overwrites that record.

This document is the log of what was changed and why. It is written for someone using the
data who has never seen the review that produced these changes.

## Conventions this branch holds to

1. **One study = one submitted folder.** Study counts are folder counts. A submission is
   never split across several top-level folders, however many sub-experiments or constructs
   it contains. *One documented exception:* `aguasvivas2018_spalex` and
   `aguasvivas2018_spalex_es` are two independent processings of the same SPALEX release
   (doi 10.3389/fpsyg.2018.02156). Both folders are kept because both are real contributions,
   but they count as **one study** in the coverage totals.
2. **One `prompts.jsonl.zip` per folder.** All of a folder's `exp*.csv` files feed a single
   prompts file.
3. **Studies with several target types keep them all.** Where a trial carries both a choice
   and a reaction time (or two RTs, or a secondary label), all of them stay marked with
   `<<...>>`. Deciding which target to model is an *analysis-time* choice, made downstream;
   it is not baked into the corpus.
4. **Fixes live in each study's own scripts.** A correction is made in that study's
   `preprocess_data.*` / `generate_prompts.*`, so re-running a study reproduces the committed
   `processed_data/` and `prompts.jsonl.zip`. There are no `*_fixed` side-files.

## What is not on this branch

Analysis notebooks, derived result tables, and the working notes from the review are
deliberately absent — they live on the analysis branch. This branch carries the corpus, each
study's own scripts, and the shared tooling in [`scripts/harmonization/`](scripts/harmonization/).

---

## Changes so far

### Git LFS integrity

Several files were tracked by an LFS rule but stored in git as plain bytes, or stored as an
LFS pointer with no rule to resolve it. Both forms of mismatch are silent: the file looks
normal in a listing, and the damage only surfaces later.

The concrete failure this caused: `guasch2023_prevalence` had **no LFS rule in any
`.gitattributes`**, upstream or local. Checking out the repo therefore wrote literal pointer
*text* to disk, and when those files were regenerated and committed, git stored 810 MB and
216 MB of raw bytes. Both exceed GitHub's 100 MB hard limit, which made the branch holding
them impossible to push. No data was lost — the bytes matched the intended LFS objects
exactly — but the branch was stuck.

| Fix | Detail |
|---|---|
| Added missing rules | `guasch2023_prevalence/*` (original_data, processed_data, prompts), `aguasvivas2018_spalex/CODEBOOK.csv` — all previously pointers with no rule |
| Case-exact `Images.zip` rule | The existing rule is spelled `images.zip`. It matched `connel2022_naming/Images.zip` only on a case-insensitive filesystem such as macOS APFS; on Linux it did not match at all, leaving a 757 MB file one regeneration away from the same failure |
| Renormalized 4 files | `balota2007_naming` and `brysbaert2014_Concreteness` prompts, `guasch2023_prevalence/original_data/sessions.csv`, `petrenco2024_associations_images/images.zip` — tracked by a rule but stored as plain blobs |
| Removed a duplicate rule | `brysbaert2014_Concreteness/processed_data/exp1.csv` appeared twice |

Verified: `git lfs fsck --pointers` reports OK, no blob in this branch's history exceeds
100 MB, and no unsmudged pointer remains in a checkout.

### Corpus corrections

| Study | Change |
|---|---|
| `guenther2020TS` | `README.md` described a 16-way semantic-relation choice task with 22,000 data points. That is a different study — `guenther2022relational`. This one is a binary sensible/not-sensible judgment on compound words, with a per-participant randomized key mapping. Corrected. |

### Reproducibility

Every dataset script is now runnable from a clean clone, from any working directory.
Before this, 44 of 66 studies could not be.

| Problem | Studies | What was wrong |
|---|---|---|
| Hardcoded absolute paths | 7 | `/Users/cyhsieh/...`, `C:/Users/ivasa/...`, `D:\PsychLing-101\...`, `F:/PsychLing/...` — each worked only on one contributor's machine |
| Output written to the working directory | 16 | `generate_prompts` wrote `prompts.jsonl` wherever it was invoked from. Running one from `/tmp` deposited a 39 MB file there |
| Working-directory assumptions | 8 | `setwd()` requiring the repo root, `rstudioapi::getActiveDocumentContext()` (cannot work outside RStudio), `here::i_am()` and `sys.frame(1)$ofile` (both silently fall back to the working directory under `Rscript`) |
| Output in the wrong folder | 3 | `exp*.csv` written to the study root instead of `processed_data/` — which broke `bonandrini2026`'s own preprocess → generate chain — and `jap2025_erp`'s archive written inside `processed_data/` |
| Required CLI argument | 1 | `connel2022_naming` exited with an argparse error when run with no arguments |
| Missing script | 1 | `Pantelidou2026_wugTest`'s preprocess script was named `preprocessed_data.py` |
| Package self-installation | 3 | `Wulff2022`'s two scripts called `install.packages("tidyverse")` unconditionally on every run |
| Writes into `original_data/` | 3 | derived files written back into the inputs, so a second run behaved differently from the first |

Dependencies are now declared in [`requirements.txt`](requirements.txt) and
[`requirements-R.txt`](requirements-R.txt); previously there was no dependency list of
any kind, and one undeclared package (`jsonlines`, imported by 27 scripts) blocked prompt
generation for 15 studies on its own. [README](README.md) states the rules a script must
follow, and records that R scripts need a UTF-8 locale — under `LC_CTYPE=C`, R escapes
non-ASCII on output and `É` is written as `<U+00C9>`.

Verification used [`scripts/harmonization/compare_prompts.py`](scripts/harmonization/compare_prompts.py),
which compares structure rather than bytes. 22 studies randomize their choice-letter
mapping without a seed, so re-running them legitimately changes almost every line; a byte
diff would hide a real regression in that noise.

### Anonymization left intact

`devardaetal2024_cloze` and `_rating` delete their identifying Excel exports after
converting them and strip identifying columns from the Prolific files in place. That is
deliberate and was preserved, not "fixed" — only guarded so it cannot rewrite already-clean
files on every run.

### Studies whose committed data cannot be regenerated

Found while verifying, and **not** worked around by guessing. In each case the committed
`processed_data` came from a different version of the script than the one in the repository,
or from inputs that are no longer present:

| Study | Why |
|---|---|
| `wang2025_lexicaldecision` | committed CSV has a different column order, and `phase_id` is `"0"` where the script necessarily produces `"0.0"` (`block` is float64 with NaN) |
| `saban2024_ldt` | committed CSVs are semicolon-delimited and carry an `age` column the script never produces |
| `Pantelidou2026_wugTest` | committed CSV holds the full `clinical_diagnoses` response text where the script produces `"No."` |
| `devardaetal2024_cloze`, `_rating` | anonymization removed `participant_id`, the key joining demographics to trials, so the demographic columns in the committed CSV can no longer be derived |
| `jap2025_erp` | needs `merged-list-1.txt` and `merged-list-2.txt`, which are in no commit |
| `Prekovicetal2016` | `preprocess_data.R` reads `VLD_stimuli_list.csv`, which is not in the repository |

Each now fails with an explanation naming what is missing, instead of an opaque error.
Resolving them needs the original contributors.

`seilerelpelt_etal2025_textratings` was on this list because its `preprocess_data.py` was
committed as a 0-byte file. It has been written and reproduces the committed `exp1.csv`
exactly, so it is resolved.

### Reaction time

Reaction time is now carried end to end wherever it genuinely exists.

**Recovered from the raw data.** Three studies read an RT column and then dropped
it when building `processed_data`, so the latencies existed in the source files and
nowhere else: `bonandrini2026_SPChumaneval` (8,149 trials), `guenther2022relational`
(22,000), `guenther2023ViSpa` (33,055).

**Recovered at the prompts layer.** Five more carried RT in `processed_data` but
omitted it from the JSONL: `tsaregorodtseva2026_mousetracking` (111,520 values
across two measures), `connel2022_naming` (25,850), `Leivada2020_manipulativeDiscourse`
(8,280), `hilton2021_comprehension` (2,920), and `wang2025_lexicaldecision`, which
emitted a single scalar per record and so discarded 376,100 of its 376,101 values.

**Standardized.** `rt` is the field name everywhere (`rt_all` and `trial_rt_ms` are
gone), it is always a flat list of numbers in milliseconds, and
`hilton2021_comprehension`'s seconds are converted. `Wulff2022_StructuralDifferences`'
nested array of arrays is flattened. Seven studies emitted `participant` rather than
the required `participant_id`. `miklashevsky2017_LDT_RussianNouns` buried its
demographics inside a `participant_info` object; they are now top-level fields.

Also restored along the way: gender, education and handedness in
`Leivada2020_manipulativeDiscourse`; handedness and device type in
`tsaregorodtseva2026_mousetracking`.

### `rt` now says which latency it is

`rt` was pooling four different measurements. A keypress latency, a voice-onset
latency, a first-fixation duration and a self-paced reading time are all "reaction
time", and nothing in the data distinguished them -- so a query across the corpus
silently mixed them.

Every study that has `rt` now also has a required `rt_measure` column naming the
measure. Across the 44 studies with `rt` that is `keypress` (38), `reading_time` (4),
`voice_onset` (3), `session_elapsed` (2), `first_fixation` (1) and
`inter_response_interval` (1). Four studies differ between their own files, so the
column varies by row rather than by folder: `frank2013_reading` (exp1 reading time,
exp2 first fixation), `hutchison2013_semantic` (exp1 keypress, exp2 voice onset),
`vergallito2020_ipsn` (exp2 keypress, exp3 voice onset) and
`Wulff2022_StructuralDifferences` (exp1/exp2 session elapsed, exp3 keypress).

Two of the six values exist to say that `rt` is **not a response latency at all**:
`session_elapsed` (`Wulff2022_StructuralDifferences` exp1 and exp2 record cumulative
time since the session began) and `inter_response_interval`
(`zemla2020_semantic_fluency` records time since the participant's previous response).
That caveat used to live only in prose; it is now a value you can filter on.

Assigning the measure meant reading each study rather than guessing from its name,
and three studies contradicted the obvious reading: `schiekiera2026_pwi_de` and
`_en` are picture-word interference but the README says the response is a button
press, and `connel2022_naming` times "image onset to recognition keypress" despite
being a naming study. Only `vergallito2020_ipsn` exp3, whose condition is
`word_naming`, is voice-onset among these.

Because the value is a constant per file, the column was appended to the committed
CSVs rather than re-running pipelines that take hours and, for the unseeded studies,
would re-roll unrelated randomness. Each study's `preprocess_data` script was patched
as well, so a clean run reproduces it; this was checked by re-running
`vergallito2020_ipsn`, `bonandrini2026_SPChumaneval` and
`Leivada2020_manipulativeDiscourse` and confirming byte-identical output. No prompts
file changes: every generator selects its metadata fields explicitly.

**A defect this surfaced.** `vergallito2020_ipsn` wrote its CSVs with `csv.DictWriter`,
which defaults to CRLF, while its committed files are LF -- so the script had never
reproduced its own output. Its three writers now set `lineterminator="\n"`.

### Two things deliberately not done

`devardalamarraetal2025_iconicity` looks like it has reaction times — `ldt_rt` and
`nt_rt`. It does not. Each has exactly one distinct value per stimulus: they are
published item-level norms borrowed from other megastudies, not latencies this
study's participants produced. Its own measure is an iconicity rating. Emitting
them as `rt` would make a rating study look like a timed one.

`Wulff2022_StructuralDifferences`' `rt` column is **not reaction time in exp1 and
exp2**. `preprocess_data.R` renames the raw `time` column to `rt`, and within a
participant the values rise monotonically (863, 1454, 2305, 3679, …) — they are
cumulative time since the session began. Per-response latencies would have to be
derived by differencing. The column is not renamed here, because that is a
vocabulary decision, but its CODEBOOK description now says precisely what the
numbers are.

### Defects found while verifying

Several scripts could not have produced the outputs committed beside them:

| Study | Defect |
|---|---|
| `bonandrini2026_SPChumaneval` | called `stream_out()` without ever loading `jsonlite`; the write step failed outright |
| `marson2026_eplep` | assembled JSON by hand, writing `NA` as a literal token and leaving 97 unparseable lines; also dropped its first column unconditionally, deleting `participant_id` |
| `aguasvivas2018_spalex` | grouped by `participant`, sorted by `trial`, read `correct` — none of which exist in its own `processed_data` |
| `lynott2020lancaster` | emitted `participant` while its committed archive carried `participant_id` |
| `Dymarska2025_associations` | concatenated an unsorted glob, making row order filesystem-dependent |

### Every study now builds its own archive

`prompts.jsonl.zip` is the form the repo tracks, but 21 of the 66 generate scripts
did not produce one — the archives beside them had been zipped by hand, so nothing
tied an archive to the script that supposedly made it. All 21 now build their own,
and the plain `.jsonl` is removed afterwards, so the tracked artifact is always the
one the script just wrote. `schiekiera2026_pwi_de` and `_en` had even documented the
manual step in their own docstrings (`Then zip the results for the PR:: zip
prompts.jsonl.zip prompts.jsonl`); that instruction is gone because the script does it.

Hand-zipping had left visible traces. Nine of the 66 committed archives were
malformed:

| Archive defect | Studies |
|---|---|
| `__MACOSX/._prompts.jsonl` resource-fork entries | `Dymarska2025_associations`, `guenther2020LDT`, `guenther2020TS`, `guenther2023associations_individual`, `guenther2023grammaticality`, `guenther2024comprehension`, `guenther2024substitutions`, `hsieh2025_rating` |
| no `prompts.jsonl` entry at all — the only member was `Users/tikhomirova/PsychLing-101/pissani2026_metaphor/prompts.jsonl`, so unzipping produced a four-deep directory tree instead of the file | `pissani2026_metaphor` |

All 66 archives now contain exactly one entry, named `prompts.jsonl`.

`pissani2026_metaphor`'s was self-inflicted: the earlier path-resolution pass gave it
`utils::zip(..., flags = "-q")`, and without `-j` the absolute path was stored.
`keuleers2010_DLP1` had the same latent fault — its committed archive predated the
change, so the defect would have appeared the next time anyone ran the script. Both
now use `flags = "-j9X"`, as every other R study does.

### Two encoding bugs, found by running the scripts

Neither is visible by reading the code.

**`devardalamarraetal2025_iconicity` shipped mojibake.** Its committed archive renders
`VANITÀ` as `VANITÃ€` and `VIRTÙ` as `VIRTÃ™` — the signature of UTF-8 bytes decoded as
Latin-1 — in 109 of its 111 records. The cause is that `generate_prompts.R` was itself
stored as Latin-1, the only non-UTF-8 file in the corpus. Read under a UTF-8 locale its
own prompt text breaks; read under a Latin-1 one, as the contributor evidently did, the
prompt text is right and every accented stimulus from the (correctly UTF-8) CSV is
corrupted instead. The script is now UTF-8 and the regenerated archive matches the
source data.

That same file had been invisible to the earlier path-resolution sweep: BSD `grep`
silently reports no matches on a file containing invalid UTF-8, so a search for bare
relative paths simply skipped it. It was still reading `processed_data/exp1.csv` from
the working directory. It now resolves from the script, like the rest.

**R's locale escapes non-ASCII output.** Run under `LC_CTYPE=C`,
`miklashevsky2017_LDT_RussianNouns` writes 60,986 `<U+0431>`-style escapes and not one
Cyrillic character; under `LC_ALL=en_US.UTF-8` the same script writes 81,164 Cyrillic
characters and zero escapes. `keuleers2010_DLP1` degrades the same way (`café` →
`caf<U+00E9>`). The README already warns about this; it is recorded here because it
silently produces a file that looks fine until you open it.

### Verifying the regenerations

All 21 were re-run from `/tmp` against a virtualenv built from `requirements.txt`, which
installs cleanly and supplies `jsonlines` — a package no interpreter on the development
machine had, and which 27 scripts import. Each result was compared to the pre-run archive
with `scripts/harmonization/compare_prompts.py`.

Every study came back either byte-identical (for the seeded ones) or structurally
equivalent, except where a change was the point: the archives that were stale with
respect to the reaction-time work (`Dymarska2025_associations`,
`miklashevsky2017_LDT_RussianNouns`, `wang2025_lexicaldecision`,
`Pantelidou2026_wugTest`) and `devardalamarraetal2025_iconicity`'s mojibake repair.

Where content came back byte-identical and the archive was already well-formed, the
committed archive is kept rather than replaced, so Git LFS is not churned to store a file
with the same contents and a new timestamp.

`marson2026_eplep` verifies as equivalent, which is the expected result and not a good
one: its 634-of-1,416 participant coverage gap is untouched by this pass and is still
open.

### Codebooks now describe their own data

Ten studies shipped a `CODEBOOK.csv` that disagreed with their data, between them
documenting **309 columns that exist in no dataset**. Five were near-verbatim copies of
the root codebook; `devardalamarraetal2025_iconicity` listed 99 entries for 44 columns.

This follows from the validator's shape rather than from carelessness. Its one
ERROR-level codebook check asks that every data column appear in the local codebook —
which copying the root satisfies for free — and nothing checks the other direction, so
entries for columns that do not exist accumulate unnoticed.

Every study codebook now lists exactly the columns in its own `processed_data`, in the
canonical `Recommended Column Name,Description` form. Eleven header spellings were in
use (`column_name,description`, `Variable,Description`, tab- and semicolon-separated);
studies carrying a useful third column (`experiment`, `file`, `type`) keep it.
`guasch2023_prevalence`'s eleven missing descriptions came from its own README, which
had documented them all along.

In the root codebook: 7 entries dropped that `chen2026transparency` left behind when it
renamed its columns, and 7 promoted that three or more studies share (`lexicality`,
`experiment`, `word`, `soa`, `session_no`, `correct_response`, `response_correct`).
`responseX` is relabelled as what it is — a naming pattern for `response1`,
`response2`, … — rather than a column anything has.

After this, no study produces a header-format or delimiter warning, and the only
codebook warnings left are the benign "column not in the main CODEBOOK", which is
expected for genuinely study-specific columns.

**One collision is documented but not yet resolved.** `correct_response` holds the
answer that would have been right; `response_correct` says whether the participant gave
it. The names are one word-order apart, and the corpus already mixes them:
`matrineztomas2026_discreteemotions` uses `response_correct` for the correct emotion
category — the opposite of its sense in the two `gatti` studies. The descriptions now
say which is which; the rename is still open.

### guasch2023_prevalence had no participant_id

It was the only study in the corpus missing the one column the validator requires at
ERROR level. Its `exp1.csv` identified rows by `session_id` alone, while
`generate_prompts.r` already grouped by that column and emitted it as `participant_id` —
so the prompts named a key the data did not contain, and the two could not be joined.
The source distributes no person-level identifier (`sessions.csv` is the
participant-level table, one row per session), so `session_id` is now named
`participant_id` throughout, with the codebook and README saying why. Regenerated end to
end: 204,645 participants and 25,171,335 bracketed responses, unchanged.

### Attribution rebuilt from the merge history

`gh` is not installed, which had blocked this; the GitHub REST API turns out to be
readable without authentication for a public repository. All 85 pull requests and 20
issues were read and cross-checked against the 64 merge commits, mapping every one of
the 66 dataset folders to the pull request that introduced it.

`CONTRIBUTING.md` is now keyed to dataset folders, one row per folder, matching the
"one submitted folder = one study" convention — so it can be checked against the
repository rather than taken on trust. What was wrong:

| Problem | Count |
|---|---|
| merged datasets still listed as "In Progress" | 17 |
| merged datasets still listed as "Open" | 3 |
| datasets with no row at all | 4 |
| the file's own heading, printed twice | 1 |
| a row citing another study's paper (Provo carried the CELER link) | 1 |

The four with no row were `lally2022_letter_identification`,
`zemla2020_semantic_fluency`, `aguasvivas2018_spalex_es` and
`matrineztomas2026_discreteemotions`. Two contributors were missing entirely: **Valmik
Nahata** (`luke2018_provo`, `adelman2014_formpriming`, `berzak2025_onestop`) and
**Raluca Rilla** (`aguasvivas2018_spalex_es`), the latter confirmed from her commit
authorship rather than inferred from her handle.

**One contributor still needs asking.** `lally2022_letter_identification` and
`zemla2020_semantic_fluency` are credited to `@dieselpunk-brazilia`, whose real name
appears nowhere readable — not in the profile, the pull requests, or the commits. Since
contributors are promised co-authorship, this is worth an email rather than a guess.

### trial_id split by what it actually meant

`trial_id` carried three incompatible meanings. It now keeps its name only where it
identifies one trial for one participant; position within a participant is
`trial_order`, and the stimulus is `item_id`. Corpus-wide: **54 `trial_order`,
16 `item_id`, 7 `trial_label`, 6 `trial_id`**.

Classification was done from each column's **derivation**, not from its values or its
codebook description, because neither separates the cases. Where presentation order is
fixed, an item id and a position index are indistinguishable by inspection — both run
1..N per participant and both map one-to-one onto the stimulus. Two studies show why
that matters:

| Study | Looks like | Actually is |
|---|---|---|
| `wang2025_lexicaldecision` | position (1..N per participant) | `factorize(df["item"])` — the item |
| `gatti2022_false_semantic_memory_pr` | an item (one stimulus per value) | `"recognition_t" + trial_order` — position |

A first, value-shaped heuristic put both in the wrong bucket: it tested only numeric
columns for per-participant consecutiveness, so string-valued order columns fell
through it.

**Three studies regenerated to no column at all.** `guenther2022relational`,
`guenther2023ViSpa` and `guenther2023grammaticality` derive the output inside
`if "trial_id" in df.columns:`, reading a raw source column of that name. Renaming the
read made the guard false, the column vanished from the output, and the script still
exited 0. Only diffing the headers caught it — the same silent-success shape as the
earlier `pissani2026` regression.

**The remaining studies, resolved.** Eighteen studies were left carrying `trial_id`
by default rather than by decision, because the derivation-based pass could not place
them. Reading each one settled all of them:

| Became | Studies | Why |
|---|---|---|
| `item_id` | the four `FilipovicDurdevic`-family studies, `keuleers2011_britishlexiconproject` | the value is fixed to the stimulus and recurs at 40–200 different positions, so it cannot be a position |
| `trial_order` | `balota2007_LDT`, `balota2007_naming`, `bonandrini2026_SPChumaneval`, `guenther2020LDT`, `guenther2020TS`, `kyroelaeinen2022_valence` | it restarts at 1 for each participant and 118–146 different stimuli share each value |
| `trial_label` | the five `gatti` studies, `matrineztomas2026_discreteemotions`, `pexman2016_calgary` | it is a constant prefix plus `trial_order` |
| unchanged | `aguasvivas2018_spalex_es`, `chen2026transparency`, `petilli2026_ami`, `pissani2026_metaphor`, `stella2026_formamentis_data`, `vergallito2020_ipsn` | genuinely one trial for one participant |

The value heuristic and the derivation disagreed again, in the direction that would
have done real damage. The four `FilipovicDurdevic` studies look like positions —
the value never repeats within a participant and is reused across them — but
`FilipovicDurdevicFeldman2024_bialphabticVLD` assigns `trial_id` straight from the raw
`item_id`/`item_code`, and in all four each stimulus has exactly one value while each
value spans dozens of presentation positions. They are items. The giveaway is that
these are morphology studies: one value groups the two alphabets of a bialphabetic
word, the three forms of an adjective, the four forms of a verb.

**A fourth name, `trial_label`.** Seven studies build `trial_id` as a constant prefix
plus the position — `"exp1_t" + trial_order`, `"recognition_t" + recog_order`. The
result is not an identifier at all: `exp1_t5` is the same string for every
participant, so joining on it silently merges different people's trials. It carries
nothing `trial_order` does not. Renamed rather than dropped, so nothing is lost, and
each codebook now says it is a label and names the real join key,
`(participant_id, trial_order)`.

`gatti2022_false_semantic_memory_pr` was already recorded above as a case the value
heuristic mis-bucketed; it belongs to this group too, and was only caught because the
`_pr` folder sits beside `gatti2022_false_semantic_memory` and both build the column
the same way.

### Two studies that had never been runnable

Both identical on `upstream/main`, so neither is a consequence of this branch.

**`hutchison2013_semantic`** asked for `all ldt subs_all trials3.xlsx` and three
siblings, but the committed files use underscores, so it could not open any of its
inputs. With the four names corrected it runs — and reproduces its committed `exp1.csv`
byte for byte across all 847,469 data rows. The filenames were the only thing wrong
with it.

**`hilton2021_comprehension`** calls `capitalize_every_n_string()`, which is defined
nowhere in the repository and appears in no commit, so it cannot have produced its
committed CSV. The script now says so at the point of failure. It also used `here()`,
which resolves against a project-root marker and fails outside the repository; that is
replaced with the script-relative form used everywhere else.

### Studies renamed at the header only

Five studies cannot be regenerated from this repository, so their committed data is
left untouched and only the column name changes: `hilton2021_comprehension`,
`saban2024_ldt`, `devardaetal2024_cloze`, `devardaetal2024_rating` and
`Prekovicetal2016` — joined by `wang2025_lexicaldecision` and `Pantelidou2026_wugTest`,
which were briefly regenerated before that was caught. `wang2025` drifted on 4,780 rows
(`rt` as `708.0` rather than `708`, and `""` where the committed file has the literal
string `nan`); `Pantelidou2026` replaces the full `clinical_diagnoses` text with `"No."`.
Every processed CSV in this pass differs from its predecessor by the header line alone.

Also resolved paths in all six Filipović-family preprocess scripts, which only ran with
the study folder as the working directory. The four not otherwise touched regenerate
byte-identically, which is what confirms the change altered nothing else.

---

## Planned, not yet applied

The review behind this branch found more than the items above. The following are specified
but **not yet implemented**; they are listed here so the current state is not mistaken for a
finished one.

- **Reproducibility.** Five studies cannot be re-run from a clean clone because their scripts
  contain absolute paths from a contributor's machine, and one reads a different study's data.
- **Naming consistency.** Nine READMEs are mis-cased (`Readme.md`, `README.MD`), which passes
  on macOS and fails on Linux; one preprocess script is named `preprocessed_data.py`; one
  study's scripts use a lowercase `.r` extension.

See the analysis branch for the full per-study findings behind each item.
