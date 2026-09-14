# preprocess_data.R
# Preprocessing script for the Dutch Lexicon Project 1 (DLP1)
# Keuleers, E., Diependaele, K., & Brysbaert, M. (2010). Frontiers in Psychology, 1, 174.
# Source data: https://osf.io/uw7t6/
#
# This script reads the raw DLP1 trial-level file in original_data/, renames
# columns to match the canonical names in CODEBOOK.csv, and writes the tidy
# CSV exp1.csv into processed_data/.

# ---- Setup -----------------------------------------------------------------

# Dependencies are declared in requirements-R.txt at the repository root and
# installed by the reader. A dataset script must not write to the user's R library.

suppressPackageStartupMessages({
  library(readr)
  library(dplyr)
})

# Resolve paths relative to this script's location so it runs from anywhere.
# sys.frame(1)$ofile is only defined under source(); under Rscript it fell back
# to getwd(), so this still required the working directory to be the study
# folder. Derive the path from the --file= argument instead, and do not setwd.
.args <- commandArgs(trailingOnly = FALSE)
SCRIPT_DIR <- dirname(sub("^--file=", "", .args[grep("^--file=", .args)]))
if (length(SCRIPT_DIR) == 0 || !nzchar(SCRIPT_DIR)) SCRIPT_DIR <- getwd()
script_dir <- SCRIPT_DIR

raw_dir <- file.path(script_dir, "original_data")
out_dir <- file.path(script_dir, "processed_data")
dir.create(out_dir, showWarnings = FALSE)

# ---- Read raw data ---------------------------------------------------------

cat("Reading raw data...\n")

# Trial-level data: one row per trial.
# The full file (dlp-trials.txt) is ~107 MB, so we use the block-50 (final
# block) version, which the original authors recommend for analyses
# unaffected by practice effects (~19,500 trials).
trials_raw <- read_tsv(
  file.path(raw_dir, "dlp-trials-block-50.txt"),
  show_col_types = FALSE
)

# ---- Tidy trial-level data -------------------------------------------------

cat("Tidying trial-level data...\n")

trials_tidy <- trials_raw |>
  transmute(
    participant_id = participant,
    trial_id       = trial,
    trial_order    = order,
    phase_id       = block,
    stimulus       = spelling,
    condition      = ifelse(lexicality == "W", "word", "nonword"),
    response       = ifelse(response == "W", "word", "nonword"),
    accuracy       = as.integer(accuracy),
    rt             = as.numeric(rt)
  )

# ---- Write output ----------------------------------------------------------

write_csv(trials_tidy, file.path(out_dir, "exp1.csv"))

cat("Done.\n")
cat("  exp1.csv: ", nrow(trials_tidy), "trial-level rows\n")
