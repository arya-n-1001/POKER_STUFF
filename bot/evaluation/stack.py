ULTRA_SHORT = "ULTRA_SHORT"   # < 6bb
SHORT = "SHORT"               # 6–12bb
PRESSURE = "PRESSURE"         # 12–20bb
MEDIUM = "MEDIUM"             # 20–40bb
STANDARD = "STANDARD"         # 40–80bb
DEEP = "DEEP"                 # 80bb+


def get_stack_zone(stack_bb: float) -> str:
    """
    Classifies stack into poker-relevant zones.
    """

    if stack_bb < 6:
        return ULTRA_SHORT
    elif stack_bb < 12:
        return SHORT
    elif stack_bb < 20:
        return PRESSURE
    elif stack_bb < 40:
        return MEDIUM
    elif stack_bb < 80:
        return STANDARD
    else:
        return DEEP

def is_short_stack(zone: str) -> bool:
    return zone in {ULTRA_SHORT, SHORT}

def is_push_fold_zone(zone: str) -> bool:
    return zone in {ULTRA_SHORT, SHORT}

def is_deep_stack(zone: str) -> bool:
    return zone == DEEP
