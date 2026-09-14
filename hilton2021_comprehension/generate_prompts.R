#
# Created by Courtney Hilton April 30 following format on https://github.com/Data-X01/PsychLing-101/blob/main/README.md
#

# libraries ---------------------------------------------------------------

library(tidyverse)
library(jsonlite)

# Resolve paths from this script's location so it runs from any working
# directory and always writes inside its own study folder.
.args <- commandArgs(trailingOnly = FALSE)
SCRIPT_DIR <- dirname(sub("^--file=", "", .args[grep("^--file=", .args)]))
if (length(SCRIPT_DIR) == 0 || !nzchar(SCRIPT_DIR)) SCRIPT_DIR <- getwd()


# load data ---------------------------------------------------------------

randomise_letters <- function(x) {
  letter_map <- setNames(sample(letters, 3), c("y", "n", "d"))
  list(
    response    = unname(letter_map[x]),
    y_remapping = letter_map[["y"]],
    n_remapping = letter_map[["n"]],
    d_remapping = letter_map[["d"]]
  )
}

exp1 <- read_csv(file.path(SCRIPT_DIR, "processed_data", "exp1.csv")) |>
  nest(.by = participant_id) |>
  mutate(
    remapping   = map(data, ~ randomise_letters(.x$response)),
    data        = map2(data, remapping, ~ mutate(.x,
      response    = .y$response,
      y_remapping = .y$y_remapping,
      n_remapping = .y$n_remapping,
      d_remapping = .y$d_remapping
    ))
  ) |>
  select(-remapping) |>
  unnest(data) |> 
  # construct trial prompt
  rowwise() |> 
  mutate(
    prompt = paste0(
      "Trial ",
      trial_order,
      ": The sentence stimuli is ",
      stimulus,
      ". The comprehension probe is '",
      comprehension_probe,
      "'. You press <<",
      response,
      ">> after <<",
      round(rt * 1000),
      ">> ms. ",
      if_else(accuracy == 1, "Correct.", "Incorrect.")
    )
  )

# instructions ------------------------------------------------------------

instructions1 <- paste(
  "Welcome to the experiment. Thank you for participating!",
  "In each trial, you will read a sentence one word at a time, presented on the screen at a steady rhythm.",
  "When words appear in all capital letters, imagine reading this word with extra rhythmic emphasis. These will occur at a regular pattern like a rhythm.",
  "After reading the sentence, the experiment then tests your understanding of this sentence by asking you a question.",
  "You respond to this question with either 'yes' or 'no', indicating your response with the 'Y_PLACEHOLDER' and 'N_PLACEHOLDER' keys respectively.",
  "If you have no idea of the answer, either because you found the sentence hard, or your concentration lapsed. Don't worry. Press 'D_PLACEHOLDER' for \"don't know\".",
  "This is totally fine, it is natural for your concentration to go up and down during an experiment like this and it's important you don't just randomly guess an answer.",
  "For example, if the sentence was \"The boy that the girl liked is wearing a hat\" and the question was \"the girl is wearing a hat\", the correct response would be 'N_PLACEHOLDER'.",
  "When the question appears on the screen, you are to respond as quickly as you can.",
  "If you take longer than 5 seconds, you will be reminded to speed up on the next trial. Accuracy is still important, however, so do not go too quickly.",
  "And unlike reading this sentence, during the trial, the sentence will flash up on the screen one or two words at a time, synchronised to an auditory tone.",
  "You control when each trial starts, so feel free to take short breaks to keep your concentration high. And you are always welcome to ask the experimenter questions during these breaks if anything is unclear.",
  "It is very important that you feel confident in your understanding of the task and are giving it your full attention. Making mistakes is part of the experiment, though, so do not worry when this happens.",
  "Good science is made possible by good participants, so thank you in advance for your cooperation—we really appreciate it!",
  "During the trials, keep your index fingers resting on the 'Y_PLACEHOLDER' and 'N_PLACEHOLDER' key ready to press the button.",
  "Press space to start the main experiment.",
  sep = " "
)

# assemble output format --------------------------------------------------

participant_ids <- unique(exp1$participant_id)

prompts <- map(participant_ids, \(.participant_id) {
  data_filtered <- exp1 |> 
    filter(participant_id == .participant_id) |> 
    arrange(trial_order)
  
  trial_prompts <- data_filtered |> 
    pull(prompt)
  
  y_key <- unique(data_filtered$y_remapping)
  n_key <- unique(data_filtered$n_remapping)
  d_key <- unique(data_filtered$d_remapping)
  
  instructions_remapped <- instructions1 |>
    str_replace_all("Y_PLACEHOLDER", y_key) |>
    str_replace_all("N_PLACEHOLDER", n_key) |>
    str_replace_all("D_PLACEHOLDER", d_key)
  
  prompt <- paste(c(instructions_remapped, trial_prompts), collapse = "\n")
  
  data.frame(
    text = prompt,
    experiment = "hilton2021_comprehension_exp1",
    participant_id = .participant_id,
    age = unique(data_filtered$age),
    gender = unique(data_filtered$gender),
    first_language = unique(data_filtered$first_language),
    other_languages = unique(data_filtered$other_languages),
    handedness = unique(data_filtered$handedness),
    country_of_residence = unique(data_filtered$country_of_residence),
    # Per-trial reaction times. processed_data stores rt in SECONDS, but the
    # prompt text above already reports round(rt * 1000) ms, and the rest of the
    # corpus uses milliseconds -- so emit ms here to match both.
    rt = I(list(round(data_filtered$rt * 1000)))
  )
}) |> 
  list_rbind()

# write to JSON lines -----------------------------------------------------

jsonl_path <- file.path(SCRIPT_DIR, "prompts.jsonl")
jsonlite::stream_out(prompts, file(jsonl_path), verbose = FALSE)

# Package the deliverable. The script previously left this to be done by hand
# ("NOTE: need to zip this separately"), so the committed archive was never
# reproducible from the script. flags="-j9X" junks directory names so the entry
# is plain "prompts.jsonl".
# COPYFILE_DISABLE stops macOS zip adding __MACOSX/._* resource-fork entries,
# which is where the stray entries in several committed archives came from.
Sys.setenv(COPYFILE_DISABLE = "1")
zip(file.path(SCRIPT_DIR, "prompts.jsonl.zip"), jsonl_path, flags = "-j9X")
file.remove(jsonl_path)

# -------------------------------------------------------------------------