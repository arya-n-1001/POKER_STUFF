from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate
from bot.config.constants import EQUITY_CALCULATION_SIMULATIONS

def calculate_equity(hole_cards, board_cards, players, simulations = EQUITY_CALCULATION_SIMULATIONS):
    """
    Returns win probability for hero hand.

    hole_cards: ['SA','DK']
    board_cards: ['H8','D7','C2']
    players: number of active players
    """

    # Safety guard
    if players <= 1:
        return 1.0

    try:
        win_rate = estimate_hole_card_win_rate(
            nb_simulation=simulations,
            nb_player=players,
            hole_card=gen_cards(hole_cards),
            community_card=gen_cards(board_cards)
        )
        return float(win_rate)

    except Exception:
        # Never crash decision loop
        return 0.0

def calculate_equity_fast(hole_cards, board_cards, players):
    """
    Lower simulation count for speed-sensitive spots.
    """
    return calculate_equity(hole_cards, board_cards, players, simulations=200)
