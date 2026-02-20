"""
Preflop ranges — TAG+ Tournament Style

Hands are stored in normalized format:
AA, AKs, AKo, 76s, etc.

Always use normalize_hand() before checking membership.
"""

from bot.config.constants import DEBUG_MODE


# ==================================================
# UNOPENED OPEN RANGES (Raise First In)
# ==================================================

OPEN_RANGES = {

    # ---------------- UTG ----------------
    "UTG": {
        "raise": {
            "77", "88", "99", "TT", "JJ", "QQ", "KK", "AA",
            "AJs", "AQs", "AKs", "KQs",
            "AQo", "AKo",
        }
    },

    # ---------------- MP ----------------
    "MP": {
        "raise": {
            "66", "77", "88", "99", "TT", "JJ", "QQ", "KK", "AA",
            "ATs", "AJs", "AQs", "AKs",
            "KJs", "KQs", "QJs",
            "AJo", "AQo", "AKo",
            "KQo",
        }
    },

    "CO": {
        "raise": {

            # All pairs
            "22","33","44","55","66","77","88","99",
            "TT","JJ","QQ","KK","AA",

            # All suited aces
            "A2s","A3s","A4s","A5s","A6s","A7s",
            "A8s","A9s","ATs","AJs","AQs","AKs",

            # Offsuit aces
            "A7o","A8o","A9o","ATo","AJo","AQo","AKo",

            # Suited kings
            "K7s","K8s","K9s","KTs","KJs","KQs",

            # Offsuit kings
            "KTo","KJo","KQo",

            # Suited queens
            "Q8s","Q9s","QTs","QJs",

            # Offsuit queens
            "Q9o","QTo",

            # Suited connectors
            "J9s","JTs",
            "T8s","T9s",
            "98s","87s","76s"
        }
    },

    # ---------------- BTN ----------------
    "BTN": {
        "raise": {

            # All pairs
            "22","33","44","55","66","77","88","99",
            "TT","JJ","QQ","KK","AA",

            # ALL suited aces
            "A2s","A3s","A4s","A5s","A6s","A7s",
            "A8s","A9s","ATs","AJs","AQs","AKs",

            # ALL offsuit aces
            "A2o","A3o","A4o","A5o","A6o","A7o",
            "A8o","A9o","ATo","AJo","AQo","AKo",

            # Suited kings
            "K2s","K3s","K4s","K5s","K6s","K7s",
            "K8s","K9s","KTs","KJs","KQs",

            # Offsuit kings (stronger)
            "K9o","KTo","KJo","KQo",

            # Suited queens
            "Q5s","Q6s","Q7s","Q8s","Q9s",
            "QTs","QJs","QKs",

            # Offsuit queens
            "Q9o","QTo","QJo",

            # Suited jacks
            "J7s","J8s","J9s","JTs",

            # Offsuit jacks
            "J9o","JTo",

            # Suited connectors & gappers
            "T8s","T9s",
            "97s","98s",
            "86s","87s",
            "76s","65s"
        }
    },

    # ---------------- SB ----------------
    "SB": {
        "raise": {
            "22", "33", "44", "55", "66", "77", "88", "99",
            "TT", "JJ", "QQ", "KK", "AA",

            "A2s", "A3s", "A4s", "A5s", "A6s", "A7s",
            "A8s", "A9s", "ATs", "AJs", "AQs", "AKs",

            "K9s", "KTs", "KJs", "KQs",
            "QTs", "QJs",
            "JTs",

            "A9o", "ATo", "AJo", "AQo", "AKo",
            "KJo", "KQo",
        }
    },
}


# ==================================================
# FACING OPEN RANGES (POSITION-AWARE)
# ==================================================

FACING_OPEN_RANGES = {

    # BTN vs CO / MP opens
    "BTN": {
        "value_3bet": {
            "TT","JJ","QQ","KK","AA",
            "AQs","AKs","AQo","AKo"
        },
        "bluff_3bet": {
            "A5s","A4s",
            "KTs","QTs",
            "JTs","T9s"
        },
        "call": {
            "22","33","44","55","66","77","88","99",
            "AJs","ATs",
            "KJs","QJs",
            "J9s","98s","87s"
        }
    },

    # SB vs BTN open (aggressive spot)
    "SB": {
        "value_3bet": {
            "99","TT","JJ","QQ","KK","AA",
            "AQs","AKs","AQo","AKo"
        },
        "bluff_3bet": {
            "A5s","A4s","A3s",
            "KTs","KJs",
            "QTs","QJs",
            "JTs","T9s"
        },
        "call": {
            "22","33","44","55","66","77","88",
            "ATs","AJs",
            "KQo","KJo"
        }
    },

    # BB vs CO open (linear)
    "BB": {
        "value_3bet": {
            "JJ","QQ","KK","AA",
            "AKs","AQs","AKo"
        },
        "bluff_3bet": {
            "A5s","A4s",
            "KTs","QTs"
        },
        "call": {
            "22","33","44","55","66","77","88","99","TT",
            "AJs","ATs",
            "KJs","KTs",
            "QJs","QTs",
            "JTs","T9s","98s","87s"
        }
    }
}
# ==================================================
# LIMPED POT ISOLATION RANGES
# ==================================================

LIMP_ISO_RANGES = {

    "BTN": {
        "raise": {

            # All pairs
            "22","33","44","55","66","77","88","99",
            "TT","JJ","QQ","KK","AA",

            # All suited aces
            "A2s","A3s","A4s","A5s","A6s","A7s",
            "A8s","A9s","ATs","AJs","AQs","AKs",

            # Suited kings
            "K7s","K8s","K9s","KTs","KJs","KQs",

            # Suited queens
            "Q8s","Q9s","QTs","QJs",

            # Suited connectors
            "J8s","J9s","JTs",
            "T8s","T9s",
            "97s","98s",
            "87s","76s",

            # Offsuit aces
            "A7o","A8o","A9o","ATo","AJo","AQo","AKo",

            # Offsuit broadways
            "KTo","KJo","KQo",
            "QTo","JTo"
        }
    },

    "CO": {
        "raise": {

            # Pairs
            "44","55","66","77","88","99",
            "TT","JJ","QQ","KK","AA",

            # Suited Aces
            "A5s","A6s","A7s","A8s","A9s",
            "ATs","AJs","AQs","AKs",

            # Suited Broadways
            "K9s","KTs","KJs","KQs",
            "Q9s","QTs","QJs",
            "J9s","JTs","T9s","98s",

            # Offsuit
            "A9o","ATo","AJo","AQo","AKo",
            "KJo","KQo"
        }
    },

    "SB": {
        "raise": {
            "66","77","88","99",
            "TT","JJ","QQ","KK","AA",

            "ATs","AJs","AQs","AKs",
            "KTs","KJs","KQs",
            "AQo","AKo"
        }
    }
}
# ==================================================
# HELPER FUNCTIONS
# ==================================================

def in_open_range(position_name: str, hand_code: str) -> bool:
    """
    True if hand is in RFI range.
    """

    if position_name not in OPEN_RANGES:
        if DEBUG_MODE:
            print(f"[RANGE] No open range for {position_name}")
        return False

    in_range = hand_code in OPEN_RANGES[position_name]["raise"]

    if DEBUG_MODE:
        print(f"[RANGE] {hand_code} in {position_name} OPEN range? {in_range}")

    return in_range


def get_facing_open_bucket(position_name: str, hand_code: str):

    if position_name not in FACING_OPEN_RANGES:
        return None

    position_ranges = FACING_OPEN_RANGES[position_name]

    if hand_code in position_ranges["value_3bet"]:
        return "value_3bet"

    if hand_code in position_ranges["bluff_3bet"]:
        return "bluff_3bet"

    if hand_code in position_ranges["call"]:
        return "call"

    return None

# ==================================================
# FACING RE-RERAISE RANGES (3-Bet Defense)
# ==================================================

FACING_RERAISE_RANGES = {

    "default": {
        "value_4bet": {
            "AA", "KK", "QQ",
            "AKs", "AKo"
        },

        "call_3bet": {
            "JJ", "TT", "99",
            "AQs", "KQs"
        },

        # Short stack jam bucket (≤20bb)
        "jam": {
            "AA", "KK", "QQ", "JJ", "TT",
            "AKs", "AKo", "AQs"
        }
    }
}
BB_DEFEND_RANGE = {
    "call": {

        # All pairs
        "22","33","44","55","66","77","88","99","TT",

        # ALL suited aces
        "A2s","A3s","A4s","A5s","A6s","A7s","A8s","A9s",
        "ATs","AJs","AQs",

        # Offsuit aces (reasonable ones)
        "A7o","A8o","A9o","ATo","AJo",

        # Suited kings
        "K2s","K3s","K4s","K5s","K6s","K7s",
        "K8s","K9s","KTs","KJs","KQs",

        # Offsuit kings
        "K9o","KTo","KJo",

        # Suited queens
        "Q5s","Q6s","Q7s","Q8s","Q9s",
        "QTs","QJs",

        # Offsuit queens
        "Q9o","QTo",

        # Suited jacks
        "J7s","J8s","J9s","JTs",

        # Suited connectors
        "T7s","T8s","T9s",
        "97s","98s",
        "86s","87s",
        "76s","65s"
    }
}

def get_facing_reraise_bucket(hand_code: str, stack_zone: str):
    """
    Returns:
        "value_4bet"
        "call_3bet"
        "jam"
        None (fold)
    """

    ranges = FACING_RERAISE_RANGES["default"]

    # Short stack jam logic
    if stack_zone in {"SHORT", "ULTRA_SHORT", "PRESSURE"}:
        if hand_code in ranges["jam"]:
            return "jam"
        return None

    # Normal stack logic
    if hand_code in ranges["value_4bet"]:
        return "value_4bet"

    if hand_code in ranges["call_3bet"]:
        return "call_3bet"

    return None

def in_limp_iso_range(position_name: str, hand_code: str) -> bool:
    if position_name not in LIMP_ISO_RANGES:
        return False

    return hand_code in LIMP_ISO_RANGES[position_name]["raise"]

def in_bb_defend_range(hand_code: str) -> bool:
    return hand_code in BB_DEFEND_RANGE["call"]


# ==================================================
# POSITION-AWARE 3BET RANGES
# ==================================================

THREE_BET_RANGES = {

    # BTN vs CO / MP opens
    "BTN": {
        "value": {
            "TT","JJ","QQ","KK","AA",
            "AQs","AKs","AQo","AKo"
        },
        "bluff": {
            "A5s","A4s",
            "KTs","QTs",
            "JTs","T9s"
        }
    },

    # SB vs BTN opens (most aggressive spot)
    "SB": {
        "value": {
            "99","TT","JJ","QQ","KK","AA",
            "AQs","AKs","AQo","AKo"
        },
        "bluff": {
            "A5s","A4s","A3s",
            "KTs","KJs",
            "QTs","QJs",
            "JTs","T9s"
        }
    },

    # BB vs CO open (more linear)
    "BB": {
        "value": {
            "JJ","QQ","KK","AA",
            "AKs","AQs","AKo"
        },
        "bluff": {
            "A5s","A4s",
            "KTs",
            "QTs"
        }
    }
}

def get_3bet_bucket(position_name: str, hand_code: str):

    if position_name not in THREE_BET_RANGES:
        return None

    if hand_code in THREE_BET_RANGES[position_name]["value"]:
        return "value"

    if hand_code in THREE_BET_RANGES[position_name]["bluff"]:
        return "bluff"

    return None


"""
Push/Fold Engine — Static Tournament Version

Used when stack is SHORT / ULTRA_SHORT / PRESSURE (≤20bb)

Returns:
    ("raise", all_in_amount)  -> JAM
    ("fold", 0)
"""

from bot.evaluation.hand_utils import normalize_hand
from bot.config.constants import DEBUG_MODE


# ==================================================
# PUSH RANGES (Tournament Baseline)
# ==================================================

PUSH_RANGES = {

    # ----------------------------------
    # BTN (Heads-up or Late)
    # ----------------------------------
    "BTN": {
        "push": {
            # All pairs
            "22","33","44","55","66","77","88","99","TT","JJ","QQ","KK","AA",

            # All aces
            "A2s","A3s","A4s","A5s","A6s","A7s","A8s","A9s",
            "ATs","AJs","AQs","AKs",
            "A2o","A3o","A4o","A5o","A6o","A7o","A8o","A9o",
            "ATo","AJo","AQo","AKo",

            # Broadways
            "K8s","K9s","KTs","KJs","KQs",
            "KTo","KJo","KQo",
            "Q9s","QTs","QJs",
            "JTs",

            # Suited connectors
            "T9s","98s","87s"
        }
    },

    # ----------------------------------
    # SB (Similar to BTN)
    # ----------------------------------
    "SB": {
        "push": {
            "22","33","44","55","66","77","88","99","TT","JJ","QQ","KK","AA",
            "A2s","A3s","A4s","A5s","A6s","A7s","A8s","A9s",
            "ATs","AJs","AQs","AKs",
            "A2o","A3o","A4o","A5o","A6o","A7o","A8o","A9o",
            "ATo","AJo","AQo","AKo",
            "K9s","KTs","KJs","KQs",
            "KTo","KJo","KQo",
            "QTs","QJs","JTs"
        }
    },

    # ----------------------------------
    # BB vs Open (Stronger Range)
    # ----------------------------------
    "BB": {
        "push": {
            "22","33","44","55","66","77","88","99","TT","JJ","QQ","KK","AA",
            "A2s","A3s","A4s","A5s","A6s","A7s","A8s","A9s",
            "ATs","AJs","AQs","AKs",
            "A2o","A3o","A4o","A5o","A6o","A7o","A8o","A9o",
            "ATo","AJo","AQo","AKo",
            "KTs","KJs","KQs",
            "QJs","JTs"
        }
    }
}


# ==================================================
# PUBLIC ENTRY
# ==================================================

def get_push_fold_action(state, valid_actions):
    """
    Determines jam/fold decision.
    """

    hand_code = normalize_hand(state.hero_cards)
    position = state.hero_position_name

    if DEBUG_MODE:
        print("\n[PUSH/FOLD ENGINE]")
        print(f"Hand: {hand_code}")
        print(f"Position: {position}")
        print(f"Stack BB: {state.stack_bb:.1f}")

    if position not in PUSH_RANGES:
        if DEBUG_MODE:
            print("No push range for this position → fold")
        return _fold(valid_actions)

    if hand_code in PUSH_RANGES[position]["push"]:
        return _jam(state, valid_actions)

    if DEBUG_MODE:
        print("Not in push range → fold")

    return _fold(valid_actions)


# ==================================================
# HELPERS
# ==================================================

def _jam(state, valid_actions):

    raise_info = next((a for a in valid_actions if a["action"] == "raise"), None)

    if not raise_info:
        return _fold(valid_actions)

    max_raise = raise_info["amount"]["max"]

    if DEBUG_MODE:
        print(f"JAM for {max_raise}")

    return "raise", max_raise


def _fold(valid_actions):
    return "fold", 0