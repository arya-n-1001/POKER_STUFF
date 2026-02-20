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