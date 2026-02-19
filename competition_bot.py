from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate
import random

class CompetitionBot(BasePokerPlayer):
    def receive_game_start_message(self, game_info):
        self.big_blind = game_info['rule']['small_blind_amount'] * 2

    def declare_action(self, valid_actions, hole_card, round_state):
        community_card = round_state['community_card']
        pot_size = round_state['pot']['main']['amount']
        
        # 1. DYNAMIC WIN RATE
        # We simulate against the number of players STILL IN THE POT, not total players.
        active_players = len([s for s in round_state['seats'] if s['state'] != 'folded'])
        win_rate = estimate_hole_card_win_rate(
            nb_simulation=1000,
            nb_player=active_players,
            hole_card=gen_cards(hole_card),
            community_card=gen_cards(community_card)
        )

        # 2. POT ODDS & "CHEAPNESS"
        call_action = [a for a in valid_actions if a['action'] == 'call'][0]
        amount_to_call = call_action['amount']
        pot_odds = amount_to_call / (pot_size + amount_to_call) if (pot_size + amount_to_call) > 0 else 0

        # 3. PRE-FLOP LOGIC (Loosened up)
        if len(community_card) == 0:
            hand_score = self._get_hand_score(hole_card)
            
            # --- BLIND DEFENSE ---
            # If we are in the Big Blind and the raise is small, we CALL almost anything
            is_blind = self._is_big_blind(round_state)
            if is_blind and amount_to_call <= self.big_blind * 2:
                return 'call', amount_to_call

            # --- AGGRESSION ---
            if hand_score >= 8: # Strong hands
                return self._smart_raise(valid_actions, self.big_blind * 3)
            
            # --- LIMPING/CALLING ---
            # If it's cheap to see a flop and we have 'okay' cards
            if amount_to_call <= self.big_blind and win_rate > 0.3:
                return 'call', amount_to_call
            
            return 'fold', 0

        # 4. POST-FLOP LOGIC (Actually playing the game)
        
        # If we have a monster, we don't just raise, we bet based on pot size
        if win_rate > 0.65:
            # Bet between 50% and 100% of the pot
            bet_amount = pot_size * random.uniform(0.5, 1.0)
            return self._smart_raise(valid_actions, bet_amount)
        
        # If we have a decent hand, we "Check-Call" (don't bet, but don't fold)
        if win_rate > pot_odds:
            return 'call', amount_to_call

        # Bluffing: 10% chance to bet if we are the last to act
        if amount_to_call == 0 and random.random() < 0.1:
            return self._smart_raise(valid_actions, pot_size * 0.5)

        return 'fold', 0

    def _is_big_blind(self, round_state):
        seats = round_state['seats']
        dealer_btn = round_state['dealer_btn']
        bb_pos = (dealer_btn + 2) % len(seats)
        return seats[bb_pos]['uuid'] == self.uuid

    def _get_hand_score(self, hole_card):
        ranks = sorted(['--23456789TJQKA'.index(c[1]) for c in hole_card], reverse=True)
        score = ranks[0]
        if hole_card[0][1] == hole_card[1][1]: score += 8 # Pair
        if hole_card[0][0] == hole_card[1][0]: score += 2 # Suited
        return score

    def _smart_raise(self, valid_actions, amount):
        raise_info = [a for a in valid_actions if a['action'] == 'raise']
        if not raise_info: return 'call', [a for a in valid_actions if a['action'] == 'call'][0]['amount']
        min_r = raise_info[0]['amount']['min']
        max_r = raise_info[0]['amount']['max']
        if min_r == -1: return 'call', [a for a in valid_actions if a['action'] == 'call'][0]['amount']
        return 'raise', max(min_r, min(max_r, int(amount)))

    def receive_game_start_message(self, game_info): pass
    def receive_round_start_message(self, r, h, s): pass
    def receive_street_start_message(self, s, r): pass
    def receive_game_update_message(self, a, r): pass
    def receive_round_result_message(self, w, h, r): pass