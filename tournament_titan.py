from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate
import random

class TournamentTitan(BasePokerPlayer):
    def receive_game_start_message(self, game_info):
        self.nb_player = game_info['player_num']
        self.big_blind = game_info['rule']['small_blind_amount'] * 2
        # Memory to store opponent stats
        self.opponents = {} 

    def receive_game_update_message(self, action, round_state):
        p_uuid = action['player_uuid']
        if p_uuid == self.uuid: return
        
        if p_uuid not in self.opponents:
            self.opponents[p_uuid] = {'fold': 0, 'raise': 0, 'call': 0, 'total_actions': 0, 'rounds_seen': 0}
        
        self.opponents[p_uuid][action['action']] += 1
        self.opponents[p_uuid]['total_actions'] += 1

    def receive_round_start_message(self, round_count, hole_card, seats):
        for p_uuid in self.opponents:
            self.opponents[p_uuid]['rounds_seen'] += 1

    def declare_action(self, valid_actions, hole_card, round_state):
        community_card = round_state['community_card']
        pot_size = round_state['pot']['main']['amount']
        stack = [s for s in round_state['seats'] if s['uuid'] == self.uuid][0]['stack']
        
        # 1. ORGANIZE DATA
        # Calculate Equity (Win %)
        win_rate = estimate_hole_card_win_rate(
            nb_simulation=1000,
            nb_player=len(round_state['seats']),
            hole_card=gen_cards(hole_card),
            community_card=gen_cards(community_card)
        )

        # Calculate Pot Odds
        call_action = [a for a in valid_actions if a['action'] == 'call'][0]
        amount_to_call = call_action['amount']
        pot_odds = amount_to_call / (pot_size + amount_to_call) if (pot_size + amount_to_call) > 0 else 0
        
        # Get Position (0=Early, 1=Mid, 2=Late/Button)
        position = self._get_position(round_state)

        # Identify Opponent Personalities
        table_has_maniac = False
        table_has_nit = False # Someone who folds too much
        for p_uuid, stats in self.opponents.items():
            if stats['total_actions'] > 5:
                aggression = (stats['raise'] + stats['call']) / stats['total_actions']
                fold_rate = stats['fold'] / stats['rounds_seen'] if stats['rounds_seen'] > 0 else 0
                if aggression > 0.8: table_has_maniac = True
                if fold_rate > 0.6: table_has_nit = True

        # 2. DECISION ENGINE
        
        # --- PRE-FLOP STRATEGY ---
        if len(community_card) == 0:
            hand_strength = self._get_preflop_strength(hole_card)
            
            # Tier 1: Monsters (AA, KK, QQ, JJ, AK)
            if hand_strength >= 9:
                return self._smart_raise(valid_actions, pot_size * 2)
            
            # Tier 2: Strong (Pairs, High Face Cards)
            if hand_strength >= 7:
                return self._smart_raise(valid_actions, self.big_blind * 3)
            
            # Tier 3: Positional Steal
            # If we are in Late position and no one has raised big yet, try to steal
            if position == 2 and amount_to_call <= self.big_blind:
                if hand_strength >= 5 or table_has_nit:
                    return self._smart_raise(valid_actions, self.big_blind * 3)
            
            # Maniac Defense: Don't fold decent hands to a maniac's min-raise
            if table_has_maniac and hand_strength >= 6 and amount_to_call < stack * 0.1:
                return 'call', amount_to_call

            # Math check for Pre-flop
            if win_rate > pot_odds + 0.1:
                return 'call', amount_to_call
            
            return 'fold', 0

        # --- POST-FLOP STRATEGY ---
        
        # A. VALUE BETTING (The "Titan" Aggression)
        if win_rate > 0.7:
            # We have a near-certain winner. Bet the whole pot.
            return self._smart_raise(valid_actions, pot_size)
        
        if win_rate > 0.55:
            # Good hand. Bet half the pot.
            return self._smart_raise(valid_actions, pot_size * 0.5)

        # B. BLUFFING & SEMI-BLUFFING
        # If we have a flush/straight draw (win rate ~35-45%) and opponent is a Nit
        if 0.35 < win_rate < 0.5 and table_has_nit:
            if random.random() < 0.25: # 25% chance to bluff
                return self._smart_raise(valid_actions, pot_size * 0.6)

        # C. THE "MATH" DEFENSE (Call based on Pot Odds)
        # We adjust our required win_rate based on whether we are playing a maniac
        threshold = pot_odds
        if table_has_maniac: threshold -= 0.05 # Call more loosely against a maniac
        
        if win_rate >= threshold:
            return 'call', amount_to_call

        # D. FINAL FOLD
        return 'fold', 0

    # --- HELPER METHODS ---

    def _get_preflop_strength(self, hole_card):
        """Returns a score from 1-10 based on hole cards"""
        ranks = sorted(['--23456789TJQKA'.index(c[1]) for c in hole_card], reverse=True)
        is_pair = ranks[0] == ranks[1]
        is_suited = hole_card[0][0] == hole_card[1][0]
        high_card = ranks[0]
        
        score = high_card / 2 # Base score
        if is_pair: score += 5
        if is_suited: score += 1
        if ranks[0] >= 13 and ranks[1] >= 10: score += 2 # Big broadway cards
        return score

    def _get_position(self, round_state):
        seats = round_state['seats']
        dealer_btn = round_state['dealer_btn']
        my_seat_idx = next(i for i, s in enumerate(seats) if s['uuid'] == self.uuid)
        dist = (my_seat_idx - dealer_btn) % len(seats)
        if dist <= 1: return 2 # Late
        if dist <= 3: return 1 # Mid
        return 0 # Early

    def _smart_raise(self, valid_actions, amount):
        raise_action = [a for a in valid_actions if a['action'] == 'raise']
        if not raise_action:
            return 'call', [a for a in valid_actions if a['action'] == 'call'][0]['amount']
        
        min_r = raise_action[0]['amount']['min']
        max_r = raise_action[0]['amount']['max']
        
        if min_r == -1: # All-in situation or engine cap
             return 'call', [a for a in valid_actions if a['action'] == 'call'][0]['amount']
             
        final_amount = max(min_r, min(max_r, int(amount)))
        return 'raise', final_amount

    def receive_street_start_message(self, street, round_state): pass
    def receive_round_result_message(self, winners, hand_info, round_state): pass