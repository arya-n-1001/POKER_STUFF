def calculate_pot_odds(to_call: float, pot: float) -> float:
    """
    Returns pot odds as a probability between 0 and 1.
    """

    if to_call <= 0:
        return 0.0

    total = pot + to_call

    if total == 0:
        return 0.0

    return to_call / total


def pot_odds_percent(to_call: float, pot: float) -> float:
    """
    Returns pot odds as percentage (0–100).
    """
    return calculate_pot_odds(to_call, pot) * 100

def break_even_equity(to_call: float, pot: float) -> float:
    """
    Minimum equity needed to call profitably.
    Alias for pot odds but semantically clearer.
    """
    return calculate_pot_odds(to_call, pot)
