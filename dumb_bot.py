from pypokerengine.players import BasePokerPlayer

class DumbBot(BasePokerPlayer):
    def declare_action(self, valid_actions, hole_card, round_state):
        community_card = round_state['community_card']
        
        # 1. Pre-flop Logic
        if len(community_card) == 0:
            ranks = [card[1] for card in hole_card]
            is_strong = ranks[0] == ranks[1] or any(r in ['A', 'K', 'Q', 'J', 'T'] for r in ranks)
            
            if is_strong:
                return self._select_action(valid_actions, 'raise')
            else:
                return self._select_action(valid_actions, 'call')

        # 2. Post-flop Logic
        hole_ranks = [card[1] for card in hole_card]
        community_ranks = [card[1] for card in community_card]
        hit_pair = any(r in community_ranks for r in hole_ranks)

        if hit_pair:
            return self._select_action(valid_actions, 'raise')
        else:
            # Check if calling is free, otherwise fold
            call_action = [a for a in valid_actions if a['action'] == 'call'][0]
            if call_action['amount'] == 0:
                return 'call', 0
            return 'fold', 0

    def _select_action(self, valid_actions, preferred_action):
        action_names = [a['action'] for a in valid_actions]
        if preferred_action in action_names:
            action = [a for a in valid_actions if a['action'] == preferred_action][0]
            if preferred_action == 'raise':
                # Return the minimum raise amount
                return action['action'], action['amount']['min']
            return action['action'], action['amount']
        
        # Fallback to call
        call_action = [a for a in valid_actions if a['action'] == 'call'][0]
        return 'call', call_action['amount']

    # --- FIXED CALLBACK SIGNATURES ---
    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass