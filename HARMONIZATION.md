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
