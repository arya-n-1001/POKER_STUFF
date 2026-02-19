from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate

class ProBot(BasePokerPlayer):
    def receive_game_start_message(self, game_info):
        self.opponents_history = {} # Track stats here

    def receive_game_update_message(self, action, round_state):
        player_uuid = action['player_uuid']
        if player_uuid == self.uuid: return # Ignore self
        
        if player_uuid not in self.opponents_history:
            self.opponents_history[player_uuid] = {'fold': 0, 'raise': 0, 'call': 0, 'total': 0}
        
        self.opponents_history[player_uuid][action['action']] += 1
        self.opponents_history[player_uuid]['total'] += 1

    def declare_action(self, valid_actions, hole_card, round_state):
        community_card = round_state['community_card']
        pot_size = round_state['pot']['main']['amount']
        
        # 1. Win Rate Simulation
        win_rate = estimate_hole_card_win_rate(
            nb_simulation=1000,
            nb_player=len(round_state['seats']),
            hole_card=gen_cards(hole_card),
            community_card=gen_cards(community_card)
        )

        # 2. Identify "The Fish" (Exploitation)
        is_someone_folding_a_lot = False
        for uuid, stats in self.opponents_history.items():
            if stats['total'] > 5: # Need a small sample size first
                fold_rate = stats['fold'] / stats['total']
                if fold_rate > 0.6: is_someone_folding_a_lot = True

        # 3. Strategy Logic
        
        # BLUFFING: If opponents are cowards (fold a lot), we raise even with bad cards
        if is_someone_folding_a_lot and win_rate < 0.35:
            # 10% chance to bluff to stay unpredictable
            import random
            if random.random() < 0.15: 
                return self._select_action(valid_actions, 'raise', pot_size * 0.5)

        # SEMI-BLUFFING: If we have a decent hand but not a pair yet
        if len(community_card) > 0 and 0.4 < win_rate < 0.6:
             return self._select_action(valid_actions, 'raise', pot_size * 0.5)

        # VALUE BETTING: We have the best hand
        if win_rate > 0.6:
            return self._select_action(valid_actions, 'raise', pot_size)

        # STANDARD CALL: Math-based
        call_action = [a for a in valid_actions if a['action'] == 'call'][0]
        amount_to_call = call_action['amount']
        pot_odds = amount_to_call / (pot_size + amount_to_call) if (pot_size + amount_to_call) > 0 else 0
        
        if win_rate >= pot_odds:
            return 'call', amount_to_call
        
        return 'fold', 0

    def _select_action(self, valid_actions, preferred_action, amount=0):
        # Prevent float issues and ensure min/max raise limits
        action_names = [a['action'] for a in valid_actions]
        if preferred_action == 'raise' and 'raise' in action_names:
            raise_info = [a for a in valid_actions if a['action'] == 'raise'][0]
            amount = max(raise_info['amount']['min'], min(raise_info['amount']['max'], int(amount)))
            return 'raise', amount
        
        # Default to call
        call_action = [a for a in valid_actions if a['action'] == 'call'][0]
        return 'call', call_action['amount']

    # More required callbacks
    def receive_round_start_message(self, round_count, hole_card, seats): pass
    def receive_street_start_message(self, street, round_state): pass
    def receive_round_result_message(self, winners, hand_info, round_state): pass