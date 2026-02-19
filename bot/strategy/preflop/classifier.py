from enum import Enum

class PreflopSituation(Enum):
    UNOPENED = "unopened"
    LIMPED = "limped_pot"
    FACING_OPEN = "facing_open"
    FACING_RERAISE = "facing_reraise"


def detect_preflop_situation(state):

    ctx = state.preflop_context
    raises = ctx["raises_before"]
    limpers = ctx["limpers_before"]

    # --- priority order matters ---

    if raises >= 2:
        return PreflopSituation.FACING_RERAISE

    if raises == 1:
        return PreflopSituation.FACING_OPEN

    if limpers > 0:
        return PreflopSituation.LIMPED

    return PreflopSituation.UNOPENED
