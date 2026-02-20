# bot/strategy/postflop/river_engine.py

import random

from bot.strategy.postflop.hand_category import categorize_hand, HandCategory
from bot.strategy.postflop.board_texture import analyze_board


# ======================================================
# PUBLIC ENTRY
# ======================================================

def get_river_action(state, valid_actions):

    texture = analyze_board(state.board_cards)
    category = categorize_hand(state)

    hero_is_aggressor = _was_preflop_aggressor(state)

    to_call = state.to_call

    # --------------------------------------------------
    # IF FACING A BET
    # --------------------------------------------------

    if to_call > 0:

        # Call with strong value
        if category in {HandCategory.NUTS, HandCategory.STRONG_MADE}:
            return _call_amount(valid_actions)

        # Bluff catcher logic
        if category == HandCategory.MEDIUM_MADE:
            if state.equity > state.pot_odds:
                return _call_amount(valid_actions)

        return "fold", 0

    # --------------------------------------------------
    # IF CHECKED TO HERO
    # --------------------------------------------------

    else:

        # Value bet
        if category in {HandCategory.NUTS, HandCategory.STRONG_MADE}:
            return _bet_medium(state, valid_actions)

        # Thin value IP
        if category == HandCategory.MEDIUM_MADE and state.in_position:
            if random.random() < 0.5:
                return _bet_small(state, valid_actions)

        # Bluff logic
        if category == HandCategory.AIR:

            # Bluff only if:
            # - Hero was aggressor
            # - In position
            # - Board is scary
            if hero_is_aggressor and state.in_position and texture.wet:
                if random.random() < 0.30:
                    return _bet_small(state, valid_actions)

        return _check_or_call(valid_actions)


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
    return _bet_fraction(state, valid_actions, 0.8)


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


def _call_amount(valid_actions):
    call_action = next(a for a in valid_actions if a["action"] == "call")
    return "call", call_action["amount"]


def _check_or_call(valid_actions):
    call_action = next(a for a in valid_actions if a["action"] == "call")
    return "call", call_action["amount"]