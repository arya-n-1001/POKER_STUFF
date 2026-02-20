# bot/strategy/postflop/board_texture.py

from collections import Counter


RANK_ORDER = "23456789TJQKA"
RANK_VALUE = {r: i for i, r in enumerate(RANK_ORDER)}


class BoardTexture:

    def __init__(
        self,
        paired,
        monotone,
        two_tone,
        connected,
        high_card_heavy,
        low_board,
        wet_score,
        dry,
        wet
    ):
        self.paired = paired
        self.monotone = monotone
        self.two_tone = two_tone
        self.connected = connected
        self.high_card_heavy = high_card_heavy
        self.low_board = low_board
        self.wet_score = wet_score
        self.dry = dry
        self.wet = wet


# ======================================================
# PUBLIC ENTRY
# ======================================================

def analyze_board(board_cards):

    if len(board_cards) < 3:
        # preflop or invalid
        return None

    ranks = [c[1] for c in board_cards]
    suits = [c[0] for c in board_cards]

    rank_counts = Counter(ranks)
    suit_counts = Counter(suits)

    # -----------------------------------------
    # BASIC STRUCTURE FLAGS
    # -----------------------------------------

    paired = any(v >= 2 for v in rank_counts.values())
    monotone = any(v >= 3 for v in suit_counts.values())
    two_tone = any(v == 2 for v in suit_counts.values())

    values = sorted([RANK_VALUE[r] for r in ranks])

    connected = _is_connected(values)

    high_card_heavy = sum(r in {"A", "K", "Q"} for r in ranks) >= 2
    low_board = max(values) <= RANK_VALUE["9"]

    # -----------------------------------------
    # WETNESS SCORING
    # -----------------------------------------

    wet_score = 0

    if connected:
        wet_score += 2

    if two_tone:
        wet_score += 2

    if monotone:
        wet_score += 3

    if not paired and connected:
        wet_score += 1

    if max(values) - min(values) <= 4:
        wet_score += 1

    dry = wet_score <= 2
    wet = wet_score >= 4

    return BoardTexture(
        paired=paired,
        monotone=monotone,
        two_tone=two_tone,
        connected=connected,
        high_card_heavy=high_card_heavy,
        low_board=low_board,
        wet_score=wet_score,
        dry=dry,
        wet=wet
    )


# ======================================================
# INTERNAL HELPERS
# ======================================================

def _is_connected(values):

    if len(values) < 3:
        return False

    gaps = []

    for i in range(len(values) - 1):
        gaps.append(values[i+1] - values[i])

    return max(gaps) <= 2