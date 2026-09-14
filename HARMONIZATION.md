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
| `seilerelpelt_etal2025_textratings` | `preprocess_data.py` is 0 bytes |

Each now fails with an explanation naming what is missing, instead of an opaque error.
Resolving them needs the original contributors.

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

**22 of 66 generate scripts still do not build their own `prompts.jsonl.zip`.** Those
archives were produced by hand and cannot be verified against the scripts beside
them. Eight studies therefore have a fixed generator but a stale committed archive;
they are regenerated when the prompt-layer work lands.

---

## Planned, not yet applied

The review behind this branch found more than the items above. The following are specified
but **not yet implemented**; they are listed here so the current state is not mistaken for a
finished one.

- **Codebook unification.** 235 of the 302 column names in use across `processed_data/` are
  absent from the root `CODEBOOK.csv`, and 13 different per-study codebook header formats are
  in circulation. Several root entries carry text copied from one specific study and are
  simply wrong elsewhere. Six studies shipped a near-verbatim copy of the root codebook
  instead of their own, producing 315 entries describing columns that do not exist in their data.
- **Reaction-time recovery.** Three studies drop an RT column that exists in their raw data
  (`bonandrini2026_SPChumaneval`, `guenther2023ViSpa`, `guenther2022relational`). Seven more
  carry RT in `processed_data/` but omit it from the prompts. One
  (`wang2025_lexicaldecision`) emits `rt` as a single number rather than a per-trial list, so
  only the last trial of each batch survives.
- **Field-name and unit standardization.** `rt` appears as `rt_all` and `trial_rt_ms` in some
  studies; `hilton2021_comprehension` stores it in seconds while everything else uses
  milliseconds; eight studies emit `participant` instead of the required `participant_id`.
- **Reproducibility.** Five studies cannot be re-run from a clean clone because their scripts
  contain absolute paths from a contributor's machine, and one reads a different study's data.
- **Naming consistency.** Nine READMEs are mis-cased (`Readme.md`, `README.MD`), which passes
  on macOS and fails on Linux; one preprocess script is named `preprocessed_data.py`; one
  study's scripts use a lowercase `.r` extension.

See the analysis branch for the full per-study findings behind each item.
