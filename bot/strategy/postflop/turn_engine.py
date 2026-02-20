# bot/strategy/postflop/turn_engine.py

import random

from bot.strategy.postflop.hand_category import categorize_hand, HandCategory
from bot.strategy.postflop.board_texture import analyze_board


# ======================================================
# PUBLIC ENTRY
# ======================================================

def get_turn_action(state, valid_actions):

    texture = analyze_board(state.board_cards)
    category = categorize_hand(state)

    hero_is_aggressor = _was_preflop_aggressor(state)

    scare_card = _is_scare_card(state)

    high_spr = state.spr >= 6
    low_spr = state.spr <= 3

    # --------------------------------------------------
    # IF HERO HAS INITIATIVE
    # --------------------------------------------------

    if hero_is_aggressor:

        # Strong made hands → value barrel
        if category == HandCategory.NUTS:
            return _bet_medium(state, valid_actions)

        if category == HandCategory.STRONG_MADE:
            if high_spr:
                return _bet_small(state, valid_actions)
            return _bet_medium(state, valid_actions)

        # Strong draws → semi-bluff if decent equity
        if category == HandCategory.STRONG_DRAW and state.equity > 0.30:
            return _bet_small(state, valid_actions)

        # Air → bluff only on scare card
        if category == HandCategory.AIR and scare_card:
            if random.random() < 0.40:
                return _bet_small(state, valid_actions)

        return _check_or_call(valid_actions)

    # --------------------------------------------------
    # IF HERO IS DEFENDER
    # --------------------------------------------------

    else:

        to_call = state.to_call

        if to_call > 0:

            if category == HandCategory.NUTS:
                return _raise_value(state, valid_actions)

            if category in {HandCategory.STRONG_MADE, HandCategory.STRONG_DRAW}:
                if state.equity > state.pot_odds:
                    return _call_amount(valid_actions)
                return "fold", 0

            return "fold", 0

        else:

            if category in {HandCategory.NUTS, HandCategory.STRONG_MADE}:
                return _bet_small(state, valid_actions)

            if category == HandCategory.STRONG_DRAW and state.equity > 0.30:
                return _bet_small(state, valid_actions)

            return _check_or_call(valid_actions)


# ======================================================
# SCARE CARD DETECTION
# ======================================================

def _is_scare_card(state):

    if len(state.board_cards) < 4:
        return False

    turn_card = state.board_cards[-1]
    rank = turn_card[1]
    suit = turn_card[0]

    board_ranks = [c[1] for c in state.board_cards[:-1]]
    board_suits = [c[0] for c in state.board_cards[:-1]]

    # High card scare
    if rank in {"A", "K"}:
        return True

    # Flush completing scare
    if board_suits.count(suit) >= 2:
        return True

    # Straight completing scare (rough heuristic)
    ranks_sorted = sorted(board_ranks + [rank])
    if len(set(ranks_sorted)) >= 4:
        return True

    return False


# ======================================================
# HELPERS
# ======================================================

def _was_preflop_aggressor(state):

    ctx = state.preflop_context

    if not ctx:
        return False

    last_raiser = ctx.get("last_raiser_uuid")
    return last_raiser == state.hero_uuid


def _bet_small(state, valid_actions):
    return _bet_fraction(state, valid_actions, 0.5)


def _bet_medium(state, valid_actions):
    return _bet_fraction(state, valid_actions, 0.75)


def _bet_fraction(state, valid_actions, fraction):

    raise_info = next((a for a in valid_actions if a["action"] == "raise"), None)

    if not raise_info:
        return _check_or_call(valid_actions)

    pot = state.pot
    target = int(pot * fraction)

    min_raise = raise_info["amount"]["min"]
    max_raise = raise_info["amount"]["max"]

    amount = max(min_raise, min(max_raise, target))

    return "raise", amount


def _raise_value(state, valid_actions):
    return _bet_medium(state, valid_actions)


def _call_amount(valid_actions):
    call_action = next(a for a in valid_actions if a["action"] == "call")
    return "call", call_action["amount"]


def _check_or_call(valid_actions):
    call_action = next(a for a in valid_actions if a["action"] == "call")
    return "call", call_action["amount"]