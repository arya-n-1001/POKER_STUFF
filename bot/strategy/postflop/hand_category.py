# bot/strategy/postflop/hand_category.py

from enum import Enum


class HandCategory(Enum):
    NUTS = "nuts"
    STRONG_MADE = "strong_made"
    MEDIUM_MADE = "medium_made"
    WEAK_MADE = "weak_made"
    STRONG_DRAW = "strong_draw"
    WEAK_DRAW = "weak_draw"
    AIR = "air"


# ======================================================
# PUBLIC ENTRY
# ======================================================

def categorize_hand(state) -> HandCategory:

    made = state.hand_info["made_hand"]
    draws = state.hand_info["draws"]
    equity = state.equity
    players = state.players
    board = state.board_cards

    # -----------------------------------------
    # MULTIWAY EQUITY ADJUSTMENT
    # -----------------------------------------
    if players > 2:
        multiway_factor = 1 + (players - 2) * 0.08
        equity *= multiway_factor

    # -----------------------------------------
    # NUTS LOGIC
    # -----------------------------------------
    if made in {"quads", "full_house"}:
        return HandCategory.NUTS

    if made == "flush" and not _board_is_paired(board):
        return HandCategory.NUTS

    if equity >= 0.85:
        return HandCategory.NUTS

    # -----------------------------------------
    # STRONG MADE
    # -----------------------------------------
    if made in {"straight", "trips"} and equity >= 0.65:
        return HandCategory.STRONG_MADE

    if made == "two_pair" and equity >= 0.60:
        return HandCategory.STRONG_MADE

    if made == "pair" and equity >= 0.65:
        return HandCategory.STRONG_MADE

    # -----------------------------------------
    # MEDIUM MADE
    # -----------------------------------------
    if made in {"two_pair", "pair"} and equity >= 0.45:
        return HandCategory.MEDIUM_MADE

    # -----------------------------------------
    # WEAK MADE
    # -----------------------------------------
    if made in {"pair", "high_card"} and equity >= 0.30:
        return HandCategory.WEAK_MADE

    # -----------------------------------------
    # DRAW LOGIC
    # -----------------------------------------
    if "flush_draw" in draws and "straight_draw" in draws:
        return HandCategory.STRONG_DRAW

    if "flush_draw" in draws and equity >= 0.35:
        return HandCategory.STRONG_DRAW

    if "straight_draw" in draws and equity >= 0.33:
        return HandCategory.STRONG_DRAW

    if draws:
        return HandCategory.WEAK_DRAW

    # -----------------------------------------
    # AIR
    # -----------------------------------------
    return HandCategory.AIR


# ======================================================
# INTERNAL HELPERS
# ======================================================

def _board_is_paired(board):

    ranks = [c[1] for c in board]

    return len(ranks) != len(set(ranks))