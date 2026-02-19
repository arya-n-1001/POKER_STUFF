from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate
import random

class SmartPokerBot(BasePokerPlayer):
    def receive_game_start_message(self, game_info):
        # Initialize player attributes based on game settings
        self.big_blind = game_info['rule']['small_blind_amount'] * 2
        self.opponents = {}
        
        # Check the seats to find the player's stack size
        for seat in game_info['seats']:
            if seat['uuid'] == self.uuid:
                self.stack_size = seat['stack']
                break  # Found the player, exit the loop

    
    def receive_game_update_message(self, action, round_state):
        # Update historical actions of opponents
        player_uuid = action['player_uuid']
        if player_uuid == self.uuid: return
        
        if player_uuid not in self.opponents:
            self.opponents[player_uuid] = {'fold': 0, 'call': 0, 'raise': 0, 'total_actions': 0}
        
        self.opponents[player_uuid][action['action']] += 1
        self.opponents[player_uuid]['total_actions'] += 1

    def declare_action(self, valid_actions, hole_card, round_state):
        community_card = round_state['community_card']
        pot_size = round_state['pot']['main']['amount']
        
        # Estimate win rate using Monte Carlo simulations
        win_rate = estimate_hole_card_win_rate(
            nb_simulation=1000,
            nb_player=len(round_state['seats']),
            hole_card=gen_cards(hole_card),
            community_card=gen_cards(community_card)
        )

        # Check if the hand is pre-flop or post-flop for strategy
        if len(community_card) == 0:
            return self._pre_flop_strategy(valid_actions, hole_card, win_rate)
        else:
            return self._post_flop_strategy(valid_actions, hole_card, community_card, pot_size, win_rate)

    def _pre_flop_strategy(self, valid_actions, hole_card, win_rate):
        # Pre-flop decision logic based on hand strength and win rate
        hand_score = self._get_hand_score(hole_card)
        
        # Determine opponent aggression
        opponent_aggression = self._calculate_opponent_aggression()
        
        if hand_score >= 9:  # Very strong hand
            return self._smart_raise(valid_actions, self.big_blind * 4)  # Aggressive raise
        elif hand_score >= 7:  # Decent hand
            if win_rate > 0.5: 
                return self._smart_raise(valid_actions, self.big_blind * 2)
            return 'call', self.big_blind  # Call instead
        elif hand_score >= 5:  # Marginal Hands
            if opponent_aggression < 0.5:
                if win_rate > 0.4:
                    return 'call', self.big_blind
                return 'fold', 0
            
            return 'fold', 0
        return 'fold', 0

    def _post_flop_strategy(self, valid_actions, hole_card, community_card, pot_size, win_rate):
        # Decision-making based on pot odds, hand strength, and win rate
        call_action = [a for a in valid_actions if a['action'] == 'call'][0]
        amount_to_call = call_action['amount']
        pot_odds = amount_to_call / (pot_size + amount_to_call) if (pot_size + amount_to_call) > 0 else 0

        # Evaluate hand strength against community cards
        if win_rate > 0.80:  # Very strong hand
            return self._smart_raise(valid_actions, pot_size)  # Bet the pot
        elif win_rate > 0.60:
            if amount_to_call == 0:
                return self._smart_raise(valid_actions, pot_size * 0.66)
            return 'call', amount_to_call
        elif win_rate > pot_odds:  # Consider pot odds
            return 'call', amount_to_call
        elif win_rate >= 0.40:  # Drawing hands
            return self._evaluate_draws(valid_actions, amount_to_call, pot_size, win_rate)
        return 'fold', 0

    def _evaluate_draws(self, valid_actions, amount_to_call, pot_size, win_rate):
        # Logic for evaluating drawing hands
        if amount_to_call > 0 and win_rate > 0.30:
            return 'call', amount_to_call
        elif amount_to_call == 0 and win_rate > 0.25:
            return self._smart_raise(valid_actions, pot_size * 0.5)  # Semi-bluff
        return 'fold', 0

    def _get_hand_score(self, hole_card):
        # Evaluate hand strength based on ranks
        ranks = sorted(['--23456789TJQKA'.index(c[1]) for c in hole_card], reverse=True)
        score = ranks[0]  # Highest card score
        if hole_card[0][1] == hole_card[1][1]: score += 10  # Pair bonus
        if hole_card[0][0] == hole_card[1][0]: score += 2  # Suited bonus
        return score

    def _smart_raise(self, valid_actions, amount):
        # Handle smart raising actions
        raise_info = [a for a in valid_actions if a['action'] == 'raise']
        if not raise_info: 
            return 'call', [a for a in valid_actions if a['action'] == 'call'][0]['amount']
        min_r = raise_info[0]['amount']['min']
        max_r = raise_info[0]['amount']['max']
        if min_r == -1: 
            return 'call', [a for a in valid_actions if a['action'] == 'call'][0]['amount']
        return 'raise', max(min_r, min(max_r, int(amount)))

    def _calculate_opponent_aggression(self):
        # Calculate the average aggression ratio of opponents
        total_aggression = 0
        num_opponents = len(self.opponents)
        for stats in self.opponents.values():
            if stats['total_actions'] > 0:
                aggression = stats['raise'] / stats['total_actions']
                total_aggression += aggression
        return total_aggression / num_opponents if num_opponents > 0 else 0

    # Boilerplate methods required by the engine
    def receive_round_start_message(self, round_count, hole_card, seats): pass
    def receive_street_start_message(self, street, round_state): pass
    def receive_round_result_message(self, winners, hand_info, round_state): pass
