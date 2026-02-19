RANK_ORDER = "23456789TJQKA"
RANK_VALUE = {r: i for i, r in enumerate(RANK_ORDER)}

def split_card(card: str):
    """
    Converts 'SA' -> ('S', 'A')
    """
    return card[0], card[1]

def normalize_hand(hole_cards):
    """
    Converts raw cards to canonical form:
    ['SA','DK'] -> 'AKo'
    ['S8','S9'] -> '98s'
    ['H7','D7'] -> '77'
    """

    if len(hole_cards) != 2:
        raise ValueError("Hole cards must contain exactly 2 cards")

    suit1, rank1 = split_card(hole_cards[0])
    suit2, rank2 = split_card(hole_cards[1])

    # Pair case
    if rank1 == rank2:
        return rank1 + rank2

    # Sort ranks high → low
    if RANK_VALUE[rank1] > RANK_VALUE[rank2]:
        high, low = rank1, rank2
        suited = suit1 == suit2
    else:
        high, low = rank2, rank1
        suited = suit1 == suit2

    # Suited or offsuit suffix
    suffix = "s" if suited else "o"

    return f"{high}{low}{suffix}"

def is_pair(hand_code: str) -> bool:
    return len(hand_code) == 2

def get_ranks(hand_code: str):
    if is_pair(hand_code):
        return hand_code[0], hand_code[1]
    return hand_code[0], hand_code[1]
