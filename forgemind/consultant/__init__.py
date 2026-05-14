"""ForgeMind consultant interface — calibrated dialog before generating outputs.

A consultant does NOT dump 17 documents blindly. It first calibrates:
  - Which discipline is this project really in?
  - Which validated variant within that discipline applies?
  - What does ForgeMind NOT cover for this specific context?
  - Does the user want to proceed under those caveats?

The session is driven by `forgemind/data/disciplines.yaml` (the taxonomy)
so it honours the same coverage / escalation rules as the EpistemicValidator.
"""

from .followup import (
    DEFAULT_TOPICS,
    FollowupSession,
    FollowupTopic,
    LoadedCalibration,
)
from .session import (
    CalibrationOutcome,
    ConsultantOption,
    ConsultantSession,
    ConsultantTurn,
)
from .variant_output import (
    instantiate_for_variant,
    write_variant_reversal_plan,
)

__all__ = [
    "CalibrationOutcome",
    "ConsultantOption",
    "ConsultantSession",
    "ConsultantTurn",
    "DEFAULT_TOPICS",
    "FollowupSession",
    "FollowupTopic",
    "LoadedCalibration",
    "instantiate_for_variant",
    "write_variant_reversal_plan",
]
