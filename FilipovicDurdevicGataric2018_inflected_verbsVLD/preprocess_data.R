# Resolve paths from this script's location so it runs from any working
# directory and always writes inside its own study folder.
.args <- commandArgs(trailingOnly = FALSE)
SCRIPT_DIR <- dirname(sub("^--file=", "", .args[grep("^--file=", .args)]))
if (length(SCRIPT_DIR) == 0 || !nzchar(SCRIPT_DIR)) SCRIPT_DIR <- getwd()
SCRIPT_DIR <- normalizePath(SCRIPT_DIR)

dat=read.csv(file.path(SCRIPT_DIR, "original_data", "FilipovicDurdevicGataric2018_inflected_verbs_VLD.csv"),T)

dim(dat)
colnames(dat)

dat$count_exp_sequence_corrected = as.numeric(dat$count_exp_sequence) - 10

dat$participant_id = dat$naziv_fajla
dat$trial_id = dat$trial_number
dat$stimulus = dat$rec
dat$trial_order = dat$count_exp_sequence_corrected
dat$lexicality = dat$leksikalnost
dat$response = dat$response
dat$accuracy = dat$correct
dat$rt = dat$response_time

df <- dat[, c("participant_id", "trial_id", "stimulus", "trial_order", "lexicality", "response", "accuracy", "rt")]
write.csv(df, file.path(SCRIPT_DIR, "processed_data", "exp1.csv"), row.names = FALSE)
