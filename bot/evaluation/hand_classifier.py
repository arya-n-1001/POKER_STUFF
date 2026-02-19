from collections import Counter
from itertools import combinations

from pypokerengine.utils.card_utils import gen_cards

RANKS = "23456789TJQKA"
RANK_TO_VALUE = {r: i for i, r in enumerate(RANKS)}

def split_card(card):
    return card[0], card[1]

def classify_hand(hole_cards, board_cards):

    all_cards = hole_cards + board_cards

    suits = []
    ranks = []

    for c in all_cards:
        s, r = split_card(c)
        suits.append(s)
        ranks.append(r)

    rank_counts = Counter(ranks)
    suit_counts = Counter(suits)

    # ---------- MADE HAND DETECTION ----------

    counts = sorted(rank_counts.values(), reverse=True)

    top = counts[0]
    second = counts[1] if len(counts) > 1 else 0

    if top == 4:
        made = "quads"
    elif top == 3 and second >= 2:
        made = "full_house"
    elif 5 in suit_counts.values():
        made = "flush"
    elif _has_straight(ranks):
        made = "straight"
    elif top == 3:
        made = "trips"
    elif top == 2 and second == 2:
        made = "two_pair"
    elif top == 2:
        made = "pair"
    else:
        made = "high_card"


    # ---------- DRAW DETECTION ----------

    draws = []

    if _has_flush_draw(all_cards):
        draws.append("flush_draw")

    if _has_straight_draw(ranks):
        draws.append("straight_draw")
    if len(board_cards) == 5:
        draws = []  # no draws possible on river
    return {
        "made_hand": made,
        "draws": draws
    }


def _has_straight(ranks):

    values = sorted(set(RANK_TO_VALUE[r] for r in ranks))

    # Handle wheel: A2345
    if set(['A','2','3','4','5']).issubset(ranks):
        return True

    for i in range(len(values) - 4):
        if values[i+4] - values[i] == 4:
            return True

    return False

def _has_flush_draw(cards):

    suits = [split_card(c)[0] for c in cards]
    counts = Counter(suits)

    return any(v == 4 for v in counts.values())

def _has_straight_draw(ranks):

    values = sorted(set(RANK_TO_VALUE[r] for r in ranks))

    # wheel draw
    wheel = {RANK_TO_VALUE[r] for r in ['A','2','3','4','5']}
    if len(wheel.intersection(values)) >= 4:
        return True

    # general detection
    for combo in combinations(values, 4):
        if max(combo) - min(combo) <= 4:
            return True

    return False
