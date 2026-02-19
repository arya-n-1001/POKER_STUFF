from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate

class MathBot(BasePokerPlayer):
    def declare_action(self, valid_actions, hole_card, round_state):
        # 1. Calculate Win Rate (Equity) using Monte Carlo
        # We simulate 1000 games to see how often we win
        win_rate = estimate_hole_card_win_rate(
            nb_simulation=1000,
            nb_player=len(round_state['seats']),
            hole_card=gen_cards(hole_card),
            acommunity_card=gen_cards(round_state['community_card'])
        )

        # 2. Calculate Pot Odds
        # Pot Odds = Amount to Call / (Total Pot + Amount to Call)
        pot_size = round_state['pot']['main']['amount']
        # Find the 'call' action to see how much we need to pay
        call_action = [a for a in valid_actions if a['action'] == 'call'][0]
        amount_to_call = call_action['amount']
        
        if (pot_size + amount_to_call) > 0:
            pot_odds = amount_to_call / (pot_size + amount_to_call)
        else:
            pot_odds = 0

        # 3. Decision Logic
        # If we have a massive advantage (e.g., > 50% win rate in 3-player), Raise!
        if win_rate > 0.5:
            return self._select_action(valid_actions, 'raise')
        
        # If the math says it's profitable to call, Call.
        elif win_rate >= pot_odds:
            return self._select_action(valid_actions, 'call')
        
        # Otherwise, Fold
        else:
            return 'fold', 0

    def _select_action(self, valid_actions, preferred_action):
        # This helper prevents the "-1" error and ensures valid moves
        action_names = [a['action'] for a in valid_actions]
        if preferred_action in action_names:
            action = [a for a in valid_actions if a['action'] == preferred_action][0]
            if preferred_action == 'raise':
                # Just raise the minimum for now to avoid complexity
                return action['action'], action['amount']['min']
            return action['action'], action['amount']
        
        # Fallback to call
        call_action = [a for a in valid_actions if a['action'] == 'call'][0]
        return 'call', call_action['amount']

    # Boilerplate methods required by the engine
    def receive_game_start_message(self, game_info): pass
    def receive_round_start_message(self, round_count, hole_card, seats): pass
    def receive_street_start_message(self, street, round_state): pass
    def receive_game_update_message(self, action, round_state): pass
    def receive_round_result_message(self, winners, hand_info, round_state): pass