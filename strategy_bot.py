from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate

class StrategyBot(BasePokerPlayer):
    def declare_action(self, valid_actions, hole_card, round_state):
        community_card = round_state['community_card']
        pot_size = round_state['pot']['main']['amount']
        
        # 1. Calculate Win Rate
        win_rate = estimate_hole_card_win_rate(
            nb_simulation=1000,
            nb_player=len(round_state['seats']),
            hole_card=gen_cards(hole_card),
            community_card=gen_cards(community_card)
        )

        # 2. Get Call Amount
        call_action = [a for a in valid_actions if a['action'] == 'call'][0]
        amount_to_call = call_action['amount']
        pot_odds = amount_to_call / (pot_size + amount_to_call) if (pot_size + amount_to_call) > 0 else 0

        # 3. Strategy Logic
        
        # PRE-FLOP STRATEGY
        if len(community_card) == 0:
            return self._handle_preflop(valid_actions, hole_card, win_rate)

        # POST-FLOP STRATEGY
        # If we have a very strong hand (> 60% win rate)
        if win_rate > 0.6:
            return self._select_action(valid_actions, 'raise', pot_size*2/3)
        
        # If we have a good hand and the price is right
        elif win_rate > pot_odds + 0.1: # Added a 10% safety buffer
            return self._select_action(valid_actions, 'call')
        
        # Otherwise, fold
        return 'fold', 0

    def _handle_preflop(self, valid_actions, hole_card, win_rate):
        """Uses win_rate to decide pre-flop aggression"""
        # Pre-flop, win rates are lower. 0.4 is actually very high for 3-player.
        if win_rate > 0.5: 
            return self._select_action(valid_actions, 'raise', amount=100) # Aggressive
        elif win_rate > 0.35:
            return self._select_action(valid_actions, 'call')
        return 'fold', 0

    def _select_action(self, valid_actions, preferred_action, amount=None):
        action_names = [a['action'] for a in valid_actions]
        
        # Handle Raising
        if preferred_action == 'raise' and 'raise' in action_names:
            raise_info = [a for a in valid_actions if a['action'] == 'raise'][0]
            # Try to raise to the suggested amount, but stay within min/max
            max_raise = raise_info['amount']['max']
            min_raise = raise_info['amount']['min']
            
            if amount is None: amount = min_raise
            
            # Ensure we don't crash by providing -1 or out of range
            target_amount = max(min_raise, min(max_raise, amount))
            if target_amount == -1: # Engine's way of saying "All-in not possible this way"
                return 'call', [a for a in valid_actions if a['action'] == 'call'][0]['amount']
                
            return 'raise', target_amount

        # Handle Calling
        if 'call' in action_names:
            return 'call', [a for a in valid_actions if a['action'] == 'call'][0]['amount']
        
        return 'fold', 0

    def receive_game_start_message(self, game_info): pass
    def receive_round_start_message(self, round_count, hole_card, seats): pass
    def receive_street_start_message(self, street, round_state): pass
    def receive_game_update_message(self, action, round_state): pass
    def receive_round_result_message(self, winners, hand_info, round_state): pass