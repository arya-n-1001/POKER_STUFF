
BTN = "BTN"
SB = "SB"
BB = "BB"
UTG = "UTG"
MP = "MP"
CO = "CO"
HJ = "HJ"   # hijack, used in larger tables


def get_position_name(relative_pos, players):

    tables = {
        2: ["BTN", "BB"],
        3: ["BTN", "SB", "BB"],
        4: ["BTN", "SB", "BB", "UTG"],
        5: ["BTN", "SB", "BB", "UTG", "CO"],
        6: ["BTN", "SB", "BB", "UTG", "MP", "CO"],
    }

    mapping = tables.get(players)

    if not mapping:
        return f"P{relative_pos}"

    return mapping[relative_pos]


def is_late_position(pos_name: str) -> bool:
    return pos_name in {CO, BTN}

def is_blind(pos_name: str) -> bool:
    return pos_name in {SB, BB}

def is_early_position(pos_name: str) -> bool:
    return pos_name == UTG
