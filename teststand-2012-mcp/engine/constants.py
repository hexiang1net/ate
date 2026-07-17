"""TestStand step group and type constants."""

STEP_GROUP_SETUP = 0
STEP_GROUP_CLEANUP = 1
STEP_GROUP_MAIN = 2

# Maps _group_name_to_idx output to API group constants:
#   "main"→0→2, "startup"→1→0, "cleanup"→2→1
STEP_GROUP_API = {
    0: 2,
    1: 0,
    2: 1,
}

STEP_GROUP_NAMES = {
    0: "Main",
    1: "Setup",
    2: "Cleanup",
}

STEP_TYPE_SEQUENCE_CALL = "SequenceCall"
