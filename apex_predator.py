from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate
import random

class ApexPredator(BasePokerPlayer):
    def receive_game_start_message(self, game_info):
        self.big_blind = game_info['rule']['small_blind_amount'] * 2
        self.opponents = {}

    def receive_game_update_message(self, action, round_state):
        p_uuid = action['player_uuid']
        if p_uuid == self.uuid: return
        if p_uuid not in self.opponents:
            self.opponents[p_uuid] = {'raise_count': 0, 'total_actions': 0}
        self.opponents[p_uuid]['total_actions'] += 1
        if action['action'] == 'raise':
            self.opponents[p_uuid]['raise_count'] += 1

    def declare_action(self, valid_actions, hole_card, round_state):
        community_card = round_state['community_card']
        pot_size = round_state['pot']['main']['amount']
        stack = [s for s in round_state['seats'] if s['uuid'] == self.uuid][0]['stack']
        
        # 1. MATHEMATICAL BASELINE
        win_rate = estimate_hole_card_win_rate(
            nb_simulation=1000,
            nb_player=len(round_state['seats']),
            hole_card=gen_cards(hole_card),
            community_card=gen_cards(community_card)
        )

        # 2. PRE-FLOP: MIXED STRATEGY (Unpredictability)
        if len(community_card) == 0:
            hand_score = self._get_hand_score(hole_card)
            
            # Monster hand? 80% Raise, 20% Slow-play (Trap)
            if hand_score >= 9:
                if random.random() < 0.8:
                    return self._smart_raise(valid_actions, self.big_blind * 4)
                return 'call', self.big_blind
            
            # Decent hand? Raise 50%
            if hand_score >= 7:
                if random.random() < 0.5:
                    return self._smart_raise(valid_actions, self.big_blind * 3)
                return 'call', self.big_blind
            
            # Marginal hand? Fold or cheap call
            if win_rate > 0.4: return 'call', self.big_blind
            return 'fold', 0

        # 3. POST-FLOP: DYNAMIC PRESSURE
        call_action = [a for a in valid_actions if a['action'] == 'call'][0]
        amount_to_call = call_action['amount']
        
        # Check for "Committed" status: If we've already put in 30% of our stack, we rarely fold
        # (This avoids being bullied out of pots we already invested in)
        
        # THE VALUE LADDER
        if win_rate > 0.8: # The Nuts
            return self._smart_raise(valid_actions, pot_size) # Bet the pot
        
        if win_rate > 0.6: # Strong Pair / Two Pair
            # If the opponent is aggressive, let them bet (Check-Call)
            # If they check, we bet 2/3rds of the pot
            if amount_to_call == 0:
                return self._smart_raise(valid_actions, pot_size * 0.66)
            return 'call', amount_to_call

        if win_rate > 0.4: # Drawing or Middle Pair
            # Pot Odds Check
            pot_odds = amount_to_call / (pot_size + amount_to_call) if (pot_size + amount_to_call) > 0 else 0
            if win_rate >= pot_odds:
                return 'call', amount_to_call

        return 'fold', 0

    def _get_hand_score(self, hole_card):
        ranks = sorted(['--23456789TJQKA'.index(c[1]) for c in hole_card], reverse=True)
        score = ranks[0]
        if hole_card[0][1] == hole_card[1][1]: score += 10 # Pair
        if hole_card[0][0] == hole_card[1][0]: score += 2 # Suited
        return score

    def _smart_raise(self, valid_actions, amount):
        raise_info = [a for a in valid_actions if a['action'] == 'raise']
        if not raise_info: return 'call', [a for a in valid_actions if a['action'] == 'call'][0]['amount']
        min_r = raise_info[0]['amount']['min']
        max_r = raise_info[0]['amount']['max']
        if min_r == -1: return 'call', [a for a in valid_actions if a['action'] == 'call'][0]['amount']
        return 'raise', max(min_r, min(max_r, int(amount)))

    def receive_round_start_message(self, round_count, hole_card, seats): pass
    def receive_street_start_message(self, street, round_state): pass
    def receive_round_result_message(self, winners, hand_info, round_state): pass