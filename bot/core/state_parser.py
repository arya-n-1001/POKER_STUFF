# bot/core/state_parser.py

from bot.config.constants import DEBUG_MODE, DEBUG_STATE
from bot.core.position import get_position_name
from bot.evaluation.stack import get_stack_zone
from bot.evaluation.pot_odds import calculate_pot_odds
from bot.evaluation.equity import calculate_equity
from bot.evaluation.hand_classifier import classify_hand
from bot.core.preflop_context import build_preflop_context


class GameState:
    def __init__(self,
                 street,
                 hero_uuid,
                 hero_position,
                 hero_position_name,
                 stack,
                 stack_zone,
                 pot,
                 to_call,
                 players,
                 hero_cards,
                 board_cards,
                 big_blind,
                 pot_odds,
                 equity,
                 hand_info,
                 hero_act_index,
                 in_position,
                 preflop_context
                 ):

        self.street = street
        self.hero_uuid = hero_uuid
        self.hero_position = hero_position
        self.hero_position_name = hero_position_name
        self.stack = stack
        self.stack_zone = stack_zone
        self.pot = pot
        self.to_call = to_call
        self.players = players
        self.hero_cards = hero_cards
        self.board_cards = board_cards
        self.big_blind = big_blind
        self.pot_odds = pot_odds
        self.equity = equity
        self.hand_info = hand_info
        self.hero_act_index = hero_act_index
        self.in_position = in_position
        self.preflop_context = preflop_context

    @property
    def stack_bb(self):
        return self.stack / self.big_blind

    @property
    def pot_bb(self):
        return self.pot / self.big_blind
    @property
    def spr(self):
        if self.pot == 0:
            return 0
        return self.stack / self.pot

def parse_state(round_state, hole_card, player_uuid, valid_actions):

    street = round_state["street"]
    board = round_state["community_card"]
    pot = round_state["pot"]["main"]["amount"]

    seats = round_state["seats"]
    hero_seat = next(s for s in seats if s["uuid"] == player_uuid)
    stack = hero_seat["stack"]

    big_blind = round_state["small_blind_amount"] * 2

    call_action = next(
        (a for a in valid_actions if a["action"] == "call"),
        None
    )
    to_call = call_action["amount"] if call_action else 0

    players_alive = sum(1 for s in seats if s["state"] == "participating")

    dealer_btn = round_state["dealer_btn"]

    # --- Active seats (stack > 0) ---
    n = len(seats)
    rotated = [(dealer_btn + i) % n for i in range(n)]

    active_rotated = [
        seats[i] for i in rotated
        if seats[i]["stack"] > 0
    ]

    relative_pos = next(
        i for i, s in enumerate(active_rotated)
        if s["uuid"] == player_uuid
    )

    position_name = get_position_name(relative_pos, len(active_rotated))

    stack_zone = get_stack_zone(stack / big_blind)
    pot_odds = calculate_pot_odds(to_call, pot)

    equity = calculate_equity(
        hole_card,
        board,
        players_alive
    )

    hand_info = classify_hand(hole_card, board)

    # --- Position order for in-position logic ---
    order = [(dealer_btn + 1 + i) % n for i in range(n)]
    alive_order = [
        seats[i] for i in order
        if seats[i]["state"] == "participating"
    ]

    hero_act_index = next(
        i for i, s in enumerate(alive_order)
        if s["uuid"] == player_uuid
    )

    in_position = hero_act_index == len(alive_order) - 1

    preflop_context = None
    if street == "preflop":
        preflop_context = build_preflop_context(round_state, player_uuid)

    if DEBUG_MODE and DEBUG_STATE:
        print("\n[STATE PARSED]")
        print(f"Street: {street}")
        print(f"Hero Cards: {hole_card}")
        print(f"Board: {board}")
        print(f"Position Index: {relative_pos}")
        print(f"Stack: {stack} ({stack/big_blind:.1f} BB)")
        print(f"Stack Zone: {stack_zone}")
        print(f"Pot: {pot} ({pot/big_blind:.1f} BB)")
        print(f"To Call: {to_call}")
        print(f"Players Alive: {players_alive}")
        print(f"Position: {position_name}")
        print(f"Pot Odds: {pot_odds:.2%}")
        print(f"Equity: {equity:.2%}")
        print(f"Made Hand: {hand_info['made_hand']}")
        print(f"Draws: {hand_info['draws']}")
        print(f"In Position: {in_position}")
        if preflop_context:
            print("Preflop Context:")
            print(f"  Raises Before: {preflop_context['raises_before']}")
            print(f"  Callers Before: {preflop_context['callers_before']}")
            print(f"  Players Left: {preflop_context['players_left_to_act']}")
            print(f"  Closing Action: {preflop_context['is_closing_action']}")
            print(f"  Limpers Before: {preflop_context['limpers_before']}")
            print(f"  Last Raiser: {preflop_context['last_raiser_uuid']}")
        print("-" * 30)

    return GameState(
        street=street,
        hero_uuid=player_uuid,
        hero_position=relative_pos,
        hero_position_name=position_name,
        stack=stack,
        stack_zone=stack_zone,
        pot=pot,
        to_call=to_call,
        players=players_alive,
        hero_cards=hole_card,
        board_cards=board,
        big_blind=big_blind,
        pot_odds=pot_odds,
        equity=equity,
        hand_info=hand_info,
        hero_act_index=hero_act_index,
        in_position=in_position,
        preflop_context=preflop_context
    )