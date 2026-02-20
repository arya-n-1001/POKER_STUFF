# bot/strategy/postflop/flop_engine.py

import random

from bot.strategy.postflop.hand_category import categorize_hand, HandCategory
from bot.strategy.postflop.board_texture import analyze_board


# ======================================================
# PUBLIC ENTRY
# ======================================================

def get_flop_action(state, valid_actions):

    texture = analyze_board(state.board_cards)
    category = categorize_hand(state)

    hero_is_aggressor = _was_preflop_aggressor(state)

    # --------------------------------------------------
    # RANGE ADVANTAGE ESTIMATION
    # --------------------------------------------------

    range_advantage = _estimate_range_advantage(state, texture, hero_is_aggressor)

    # --------------------------------------------------
    # DECISION TREE
    # --------------------------------------------------

    if hero_is_aggressor:
        return _aggressor_strategy(
            state,
            valid_actions,
            category,
            texture,
            range_advantage,
            hero_is_aggressor
        )
    else:
        return _defender_strategy(state, valid_actions, category, texture, range_advantage)


# ======================================================
# AGGRESSOR STRATEGY (C-BET LOGIC)
# ======================================================

def _aggressor_strategy(state, valid_actions, category, texture,
                        range_advantage, hero_is_aggressor):

    nut_advantage = _estimate_nut_advantage(state, texture, hero_is_aggressor)

    high_spr = state.spr >= 6
    mid_spr = 3 <= state.spr < 6

    # ==================================================
    # HIGH NUT ADVANTAGE → POLAR STRATEGY
    # ==================================================
    if nut_advantage >= 0.6:

        # HIGH SPR → tighten stack-off threshold
        if high_spr:
            if category == HandCategory.NUTS:
                return _bet_large(state, valid_actions)

            if category == HandCategory.STRONG_MADE:
                return _bet_medium(state, valid_actions)

            if category == HandCategory.STRONG_DRAW:
                return _bet_small(state, valid_actions)

            if category == HandCategory.AIR and random.random() < 0.30:
                return _bet_small(state, valid_actions)

            return _check_or_call(valid_actions)

        # LOW / MID SPR → allow aggression
        else:
            if category == HandCategory.NUTS:
                return _bet_large(state, valid_actions)

            if category == HandCategory.STRONG_MADE:
                return _bet_medium(state, valid_actions)

            if category == HandCategory.STRONG_DRAW:
                return _bet_large(state, valid_actions)

            if category == HandCategory.AIR and random.random() < 0.45:
                return _bet_large(state, valid_actions)

            return _check_or_call(valid_actions)

    # ==================================================
    # MEDIUM NUT ADVANTAGE
    # ==================================================
    if 0.45 <= nut_advantage < 0.6:

        if category == HandCategory.NUTS:
            return _bet_medium(state, valid_actions)

        if category == HandCategory.STRONG_MADE:
            return _bet_small(state, valid_actions)

        if category == HandCategory.STRONG_DRAW:
            return _bet_small(state, valid_actions)

        if category == HandCategory.AIR and random.random() < 0.25:
            return _bet_small(state, valid_actions)

        return _check_or_call(valid_actions)

    # ==================================================
    # LOW NUT ADVANTAGE
    # ==================================================
    if nut_advantage < 0.45:

        if category == HandCategory.NUTS:
            return _bet_medium(state, valid_actions)

        if category == HandCategory.STRONG_DRAW and texture.wet:
            return _bet_small(state, valid_actions)

        return _check_or_call(valid_actions)
# ======================================================
# DEFENDER STRATEGY
# ======================================================

def _defender_strategy(state, valid_actions, category, texture, range_advantage):

    to_call = state.to_call
    high_spr = state.spr >= 6

    # Facing bet
    if to_call > 0:

        # HIGH SPR → do NOT stack off light
        if high_spr:
            if category == HandCategory.NUTS:
                return _raise_for_value(state, valid_actions)

            if category in {HandCategory.STRONG_MADE, HandCategory.STRONG_DRAW}:
                return _call_amount(valid_actions)

            if state.equity > state.pot_odds:
                return _call_amount(valid_actions)

            return "fold", 0

        # LOW / MID SPR → allow aggression
        else:
            if category in {HandCategory.NUTS, HandCategory.STRONG_MADE}:
                return _raise_for_value(state, valid_actions)

            if category == HandCategory.STRONG_DRAW:
                return _call_amount(valid_actions)

            if state.equity > state.pot_odds:
                return _call_amount(valid_actions)

            return "fold", 0

    # Checked to us
    else:

        if category == HandCategory.NUTS:
            return _bet_medium(state, valid_actions)

        if category == HandCategory.STRONG_MADE:
            return _bet_small(state, valid_actions)

        if category == HandCategory.STRONG_DRAW and texture.wet:
            return _bet_small(state, valid_actions)

        return _check_or_call(valid_actions)


# ======================================================
# RANGE ADVANTAGE ESTIMATION
# ======================================================

def _estimate_range_advantage(state, texture, hero_is_aggressor):

    advantage = 0.5

    if hero_is_aggressor:
        advantage += 0.1

    if texture.high_card_heavy:
        advantage += 0.1

    if texture.low_board and not hero_is_aggressor:
        advantage += 0.1

    if texture.paired:
        advantage += 0.05

    if texture.wet:
        advantage -= 0.1

    return max(0, min(1, advantage))


# ======================================================
# HELPERS
# ======================================================

def _was_preflop_aggressor(state):

    ctx = state.preflop_context

    if not ctx:
        return False

    last_raiser = ctx.get("last_raiser_uuid")

    if not last_raiser:
        return False

    # Hero is aggressor only if hero was last raiser
    return last_raiser == state.hero_uuid

def _bet_small(state, valid_actions):
    return _bet_fraction(state, valid_actions, 0.33)


def _bet_medium(state, valid_actions):
    return _bet_fraction(state, valid_actions, 0.66)


def _bet_large(state, valid_actions):
    return _bet_fraction(state, valid_actions, 1.0)


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


def _raise_for_value(state, valid_actions):

    # High SPR → avoid huge raises
    if state.spr >= 6:
        return _bet_small(state, valid_actions)

    return _bet_medium(state, valid_actions)

def _call_amount(valid_actions):
    call_action = next(a for a in valid_actions if a["action"] == "call")
    return "call", call_action["amount"]


def _check_or_call(valid_actions):
    call_action = next(a for a in valid_actions if a["action"] == "call")
    return "call", call_action["amount"]    

# ======================================================
# NUT ADVANTAGE ESTIMATION
# ======================================================

def _estimate_nut_advantage(state, texture, hero_is_aggressor):

    advantage = 0.5

    # Paired boards favor aggressor
    if texture.paired and hero_is_aggressor:
        advantage += 0.15

    # High card boards favor preflop raiser
    if texture.high_card_heavy and hero_is_aggressor:
        advantage += 0.15

    # Monotone boards favor aggressor (range stronger)
    if texture.monotone and hero_is_aggressor:
        advantage += 0.10

    # Low connected boards favor defender
    if texture.connected and texture.low_board and not hero_is_aggressor:
        advantage += 0.15

    # Wet boards reduce nut clarity
    if texture.wet:
        advantage -= 0.10

    return max(0, min(1, advantage))