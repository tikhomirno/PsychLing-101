# Resolve paths from this script's location so it runs from any working
# directory and always writes inside its own study folder.
.args <- commandArgs(trailingOnly = FALSE)
SCRIPT_DIR <- dirname(sub("^--file=", "", .args[grep("^--file=", .args)]))
if (length(SCRIPT_DIR) == 0 || !nzchar(SCRIPT_DIR)) SCRIPT_DIR <- getwd()
SCRIPT_DIR <- normalizePath(SCRIPT_DIR)

dat=read.csv(file.path(SCRIPT_DIR, "original_data", "FilipovicDurdevicMilin2019.csv"),T)

dim(dat)
colnames(dat)

library(dplyr)

dat <- dat %>%
  group_by(naziv_fajla) %>%
  mutate(count_exp_sequence_corrected = dense_rank(count_exp_sequence)) %>%
  ungroup()


dat$list = dat$exp_title
dat$participant_id = dat$naziv_fajla
# trial_number is fixed to the stimulus and recurs at many different
# presentation positions, so it identifies the item, not the trial.
dat$item_id = dat$trial_number
dat$stimulus = dat$rec
dat$trial_order = dat$count_exp_sequence_corrected
dat$lexicality = dat$leksikalnost
dat$response = dat$response
dat$accuracy = dat$correct
dat$rt = dat$response_time

df <- dat[, c("list", "participant_id", "item_id", "stimulus", "trial_order", "lexicality", "response", "accuracy", "rt")]
df$rt_measure <- "keypress"
write.csv(df, file.path(SCRIPT_DIR, "processed_data", "exp1.csv"), row.names = FALSE)



