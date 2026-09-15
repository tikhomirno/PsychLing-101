# Resolve paths from this script's location so it runs from any working
# directory and always writes inside its own study folder.
.args <- commandArgs(trailingOnly = FALSE)
SCRIPT_DIR <- dirname(sub("^--file=", "", .args[grep("^--file=", .args)]))
if (length(SCRIPT_DIR) == 0 || !nzchar(SCRIPT_DIR)) SCRIPT_DIR <- getwd()
SCRIPT_DIR <- normalizePath(SCRIPT_DIR)

dat=read.csv(file.path(SCRIPT_DIR, "original_data", "Prekovicetal2016.csv"),T)


dim(dat)
colnames(dat)


VLDlista = read.csv(file.path(SCRIPT_DIR, "VLD_stimuli_list.csv"), F)
dat <- dat[dat$rec %in% VLDlista[[1]], ]
dim(dat)
head(dat)



dat$participant_id = dat$Subject
dat$item_id = dat$Trial.name
dat$stimulus = dat$rec
dat$trial_order = dat$Trial.order
dat$lexicality = dat$leksikalnost
dat$letter_order = dat$FWD_BCW
dat$response = dat$response
dat$accuracy = dat$correct
dat$rt = dat$RT


df <- dat[, c("participant_id", "item_id", "stimulus",  "trial_order", "lexicality", "letter_order",  "response", "accuracy", "rt")]
dim(df)


df$rt_measure <- "keypress"
write.csv(df, file.path(SCRIPT_DIR, "processed_data", "exp1.csv"), row.names = FALSE)


