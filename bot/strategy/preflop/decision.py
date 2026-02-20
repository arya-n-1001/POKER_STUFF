"""
Preflop decision engine — TAG+ Tournament Style

Handles:
- Unopened pots
- Facing open raises
- Structured 3-betting
- Debug instrumentation
"""

from bot.strategy.preflop.classifier import (
    PreflopSituation,
    detect_preflop_situation
)

from bot.strategy.preflop.ranges import (
    in_open_range,
    get_facing_open_bucket
)

from bot.evaluation.hand_utils import normalize_hand
from bot.config.constants import DEBUG_MODE
from bot.evaluation.stack import is_push_fold_zone
from bot.strategy.preflop.ranges import get_push_fold_action
from bot.strategy.preflop.ranges import get_facing_reraise_bucket
from bot.core.state_parser import GameState
from bot.strategy.preflop.ranges import in_limp_iso_range
from bot.strategy.preflop.ranges import in_bb_defend_range
from bot.strategy.preflop.ranges import get_3bet_bucket
# ==================================================
# PUBLIC ENTRY POINT
# ==================================================

def get_preflop_action(state, valid_actions):
    """
    Returns (action, amount)
    """

    situation = detect_preflop_situation(state)
    hand_code = normalize_hand(state.hero_cards)
    position = state.hero_position_name

    if DEBUG_MODE:
        print("\n==============================")
        print("[PRE-FLOP DECISION ENGINE]")
        print(f"Hand Code: {hand_code}")
        print(f"Position: {position}")
        print(f"Stack Zone: {state.stack_zone}")
        print(f"Situation: {situation.value}")
        print("==============================")
        
    # -----------------------------
    # PUSH/FOLD OVERRIDE (≤20bb)
    # -----------------------------
    if is_push_fold_zone(state.stack_zone) and situation != PreflopSituation.FACING_RERAISE:
        return get_push_fold_action(state, valid_actions)
    
    # -----------------------------
    # UNOPENED
    # -----------------------------
    if situation == PreflopSituation.UNOPENED:
        return _handle_unopened(state, valid_actions, position, hand_code)

    # -----------------------------
    # FACING OPEN
    # -----------------------------
    if situation == PreflopSituation.FACING_OPEN:
        return _handle_facing_open(state, valid_actions, position, hand_code)
    # -----------------------------
    # FACING RERAISE
    # -----------------------------
    if situation == PreflopSituation.FACING_RERAISE:
        return _handle_facing_reraise(
            state,
            valid_actions,
            state.hero_position_name,
            hand_code
        )
    # -----------------------------
    # FACING LIMPED
    # -----------------------------    
    if situation == PreflopSituation.LIMPED:
        return _handle_limped(state, valid_actions, position, hand_code)
    # -----------------------------
    # OTHER (Not implemented yet)
    # -----------------------------
    if DEBUG_MODE:
        print("[INFO] Situation not implemented yet → default action")

    return _default_action(valid_actions)


# ==================================================
# UNOPENED LOGIC
# ==================================================

def _handle_unopened(state, valid_actions, position, hand_code):

    in_range = in_open_range(position, hand_code)
    # If we are BB and no one raised, we just check
    if position == "BB":
        if DEBUG_MODE:
            print("BB unopened spot → CHECK")
        return _call_amount(valid_actions)
    if DEBUG_MODE:
        print("[UNOPENED SPOT]")
        print(f"In opening range? {in_range}")

    if in_range:
        return _raise_standard(state, valid_actions)

    if DEBUG_MODE:
        print("Hand not in range → folding/checking")

    return _fold_or_check(valid_actions)


# ==================================================
# FACING OPEN LOGIC
# ==================================================

def _handle_facing_open(state, valid_actions, position, hand_code):

    bucket = get_facing_open_bucket(position, hand_code)
    callers = state.preflop_context["callers_before"]

    if callers >= 1:
        return _handle_squeeze_spot(state, valid_actions, position, hand_code)
    if DEBUG_MODE:
        print("[FACING OPEN SPOT]")
        print(f"Bucket: {bucket}")

    # BB defend override (kept)
    if position == "BB":
        if in_bb_defend_range(hand_code):
            if DEBUG_MODE:
                print("[BB DEFENSE] Calling")
            return _call_amount(valid_actions)

    if bucket in {"value_3bet", "bluff_3bet"}:
        return _raise_3bet(state, valid_actions)

    if bucket == "call":
        return _call_amount(valid_actions)

    if DEBUG_MODE:
        print("Not in facing range → folding")

    return _fold_or_check(valid_actions)


# ==================================================
# ACTION HELPERS
# ==================================================

def _raise_standard(state, valid_actions):
    """
    Standard tournament open size: 2.2x BB
    """

    raise_info = next((a for a in valid_actions if a["action"] == "raise"), None)

    if not raise_info:
        if DEBUG_MODE:
            print("[WARNING] Raise not available → fallback to call")
        return _call_amount(valid_actions)

    min_raise = raise_info["amount"]["min"]
    max_raise = raise_info["amount"]["max"]

    target = int(state.big_blind * 2.2)
    amount = max(min_raise, min(max_raise, target))

    if amount == -1:
        if DEBUG_MODE:
            print("[WARNING] Invalid raise amount → fallback to call")
        return _call_amount(valid_actions)

    if DEBUG_MODE:
        print("[OPEN RAISE]")
        print(f"Target: {target}")
        print(f"Final size: {amount}")
        print(f"BB Multiplier: {amount / state.big_blind:.2f}x")

    return "raise", amount


def _raise_3bet(state, valid_actions):
    """
    TAG+ 3-bet sizing:
    - 3x open when IP
    - 3.5x open when OOP
    """

    raise_info = next((a for a in valid_actions if a["action"] == "raise"), None)

    if not raise_info:
        if DEBUG_MODE:
            print("[WARNING] Cannot 3-bet → fallback call")
        return _call_amount(valid_actions)

    min_raise = raise_info["amount"]["min"]
    max_raise = raise_info["amount"]["max"]

    open_size = state.to_call
    multiplier = 3.0 if state.in_position else 3.5

    target = int(open_size * multiplier)
    amount = max(min_raise, min(max_raise, target))

    if DEBUG_MODE:
        print("[3-BET]")
        print(f"Open size: {open_size}")
        print(f"Multiplier: {multiplier}")
        print(f"Target: {target}")
        print(f"Final size: {amount}")

    return "raise", amount


def _fold_or_check(valid_actions):

    call_action = next((a for a in valid_actions if a["action"] == "call"), None)

    if call_action and call_action["amount"] == 0:
        if DEBUG_MODE:
            print("No bet → CHECK")
        return "call", 0

    if any(a["action"] == "fold" for a in valid_actions):
        if DEBUG_MODE:
            print("FOLD")
        return "fold", 0

    if DEBUG_MODE:
        print("[WARNING] No fold option → forced call")

    return _call_amount(valid_actions)


def _call_amount(valid_actions):
    call_action = next(a for a in valid_actions if a["action"] == "call")

    if DEBUG_MODE:
        print(f"CALL {call_action['amount']}")

    return "call", call_action["amount"]


def _default_action(valid_actions):

    if DEBUG_MODE:
        print("[DEFAULT ACTION] Fallback used")

    return _fold_or_check(valid_actions)

def _handle_facing_reraise(state, valid_actions, position, hand_code):
    ctx = state.preflop_context
    raises = ctx["raises_before"]

    HARD_CAP_PREMIUM = {"AA", "KK", "QQ", "AKs", "AKo"}

    if raises >= 3:
        if DEBUG_MODE:
            print("[HARD CAP ACTIVATED] Raises >= 3")

        if hand_code in HARD_CAP_PREMIUM:
            if DEBUG_MODE:
                print("Premium hand → JAM")
            return _jam_all_in(valid_actions)

        if DEBUG_MODE:
            print("Not premium → FOLD")

        return _fold_or_check(valid_actions)
    if DEBUG_MODE:
        print("[FACING RE-RERAISE SPOT]")

    # Strong 4bet hands
    value_4bet = {
        "QQ","KK","AA",
        "AKs","AKo"
    }

    # Call 3bet (only in position, deep)
    call_3bet = {
        "JJ","TT","AQs"
    }

    # Short stack override
    if state.stack_zone in {"ULTRA_SHORT", "SHORT"}:
        if hand_code in value_4bet:
            if DEBUG_MODE:
                print("Short stack strong hand → JAM")
            return _jam_all_in(valid_actions)
        if DEBUG_MODE:
            print("Short stack weak → fold")
        return _fold_or_check(valid_actions)

    # Deep stack logic
    if hand_code in value_4bet:
        if DEBUG_MODE:
            print("Value 4bet")
        return _raise_4bet(state, valid_actions)

    if state.in_position and hand_code in call_3bet:
        if DEBUG_MODE:
            print("Flat 3bet in position")
        return _call_amount(valid_actions)

    if DEBUG_MODE:
        print("Not strong enough → FOLD")

    return _fold_or_check(valid_actions)

def _raise_4bet(state, valid_actions):

    raise_info = next((a for a in valid_actions if a["action"] == "raise"), None)

    if not raise_info:
        return _call_amount(valid_actions)

    min_raise = raise_info["amount"]["min"]
    max_raise = raise_info["amount"]["max"]

    # Estimate opponent 3-bet size
    three_bet_size = state.to_call

    target = int(three_bet_size * 2.2)

    amount = max(min_raise, min(max_raise, target))

    if DEBUG_MODE:
        print("[4-BET]")
        print(f"3bet size: {three_bet_size}")
        print(f"Target 4bet: {target}")
        print(f"Final: {amount}")

    return "raise", amount

def _jam_all_in(valid_actions):

    raise_info = next((a for a in valid_actions if a["action"] == "raise"), None)
    call_action = next((a for a in valid_actions if a["action"] == "call"), None)

    if raise_info and raise_info["amount"]["max"] != -1:
        return "raise", raise_info["amount"]["max"]

    if call_action:
        return "call", call_action["amount"]

    return "fold", 0

def _handle_limped(state, valid_actions, position, hand_code):

    if DEBUG_MODE:
        print("[LIMPED POT SPOT]")

    # BB special case → check unless strong
    if position == "BB":
        if DEBUG_MODE:
            print("BB limped pot → check")
        return _fold_or_check(valid_actions)

    in_range = in_limp_iso_range(position, hand_code)

    if DEBUG_MODE:
        print(f"In iso range? {in_range}")

    if in_range:
        return _raise_limp_iso(state, valid_actions)

    if DEBUG_MODE:
        print("Not isolating → check/fold")

    return _fold_or_check(valid_actions)

def _raise_limp_iso(state, valid_actions):

    raise_info = next((a for a in valid_actions if a["action"] == "raise"), None)

    if not raise_info:
        return _call_amount(valid_actions)

    min_raise = raise_info["amount"]["min"]
    max_raise = raise_info["amount"]["max"]

    # Standard iso size = 4x BB
    target = int(state.big_blind * 4)

    amount = max(min_raise, min(max_raise, target))

    if DEBUG_MODE:
        print("[LIMP ISOLATION RAISE]")
        print(f"Target: {target}")
        print(f"Final: {amount}")

    return "raise", amount

def _handle_squeeze_spot(state, valid_actions, position, hand_code):

    if DEBUG_MODE:
        print("[SQUEEZE SPOT]")
        print(f"Callers before: {state.preflop_context['callers_before']}")

    # Only squeeze strong value
    strong_value = {
        "QQ","KK","AA",
        "AKs","AKo"
    }

    medium_value = {
        "JJ","TT","AQs","AQo"
    }

    if hand_code in strong_value:
        if DEBUG_MODE:
            print("Strong value → squeeze")
        return _raise_3bet(state, valid_actions)

    if hand_code in medium_value:
        if DEBUG_MODE:
            print("Medium value → call")
        return _call_amount(valid_actions)

    if DEBUG_MODE:
        print("Too weak multiway → fold")

    return _fold_or_check(valid_actions)