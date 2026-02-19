from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate
import random

class SuperBot(BasePokerPlayer):
    def receive_game_start_message(self, game_info):
        self.nb_player = game_info['player_num']
        self.opponents_stats = {} # Track stats of every player

    def receive_game_update_message(self, action, round_state):
        # Tracking Opponent Behavior
        p_uuid = action['player_uuid']
        if p_uuid == self.uuid: return
        
        if p_uuid not in self.opponents_stats:
            self.opponents_stats[p_uuid] = {'actions': [], 'vpip': 0, 'total_rounds': 0}
        
        self.opponents_stats[p_uuid]['actions'].append(action['action'])

    def receive_round_start_message(self, round_count, hole_card, seats):
        for p_uuid in self.opponents_stats:
            self.opponents_stats[p_uuid]['total_rounds'] += 1

    def declare_action(self, valid_actions, hole_card, round_state):
        community_card = round_state['community_card']
        pot_size = round_state['pot']['main']['amount']
        
        # 1. CORE MATH (Equity)
        win_rate = estimate_hole_card_win_rate(
            nb_simulation=1000,
            nb_player=len(round_state['seats']),
            hole_card=gen_cards(hole_card),
            community_card=gen_cards(community_card)
        )

        # 2. POT ODDS
        call_action = [a for a in valid_actions if a['action'] == 'call'][0]
        amount_to_call = call_action['amount']
        pot_odds = amount_to_call / (pot_size + amount_to_call) if (pot_size + amount_to_call) > 0 else 0

        # 3. OPPONENT MODELING (Maniac Detection)
        is_maniac_in_pot = False
        for p_uuid, stats in self.opponents_stats.items():
            if stats['total_rounds'] > 5:
                # If they raise or call > 80% of the time, they are a maniac
                aggression = (stats['actions'].count('raise') + stats['actions'].count('call')) / len(stats['actions'])
                if aggression > 0.8:
                    is_maniac_in_pot = True

        # 4. DECISION LOGIC
        
        # A. Value Betting (We have the nuts)
        if win_rate > 0.6:
            # Bet big: Pot size or at least 3x the big blind
            return self._smart_raise(valid_actions, pot_size)

        # B. Maniac Defense
        # If we are playing a maniac, we lower our standards. 
        # We call more often because we know they are probably bluffing.
        if is_maniac_in_pot and win_rate > 0.35:
            return 'call', amount_to_call

        # C. Semi-Bluffing (Decent hand + high pot odds)
        if 0.4 < win_rate < 0.6:
            # 20% chance to raise to keep them guessing
            if random.random() < 0.20:
                return self._smart_raise(valid_actions, pot_size * 0.5)
            return 'call', amount_to_call

        # D. The "Golden Rule" (Math check)
        if win_rate >= pot_odds:
            return 'call', amount_to_call

        # E. Default to Fold
        return 'fold', 0

    def _smart_raise(self, valid_actions, amount):
        # Ensures raises are always valid and integers
        raise_action = [a for a in valid_actions if a['action'] == 'raise'][0]
        min_raise = raise_action['amount']['min']
        max_raise = raise_action['amount']['max']
        
        # Never raise less than the minimum
        final_amount = max(min_raise, min(max_raise, int(amount)))
        return 'raise', final_amount

    # Boilerplate
    def receive_street_start_message(self, street, round_state): pass
    def receive_round_result_message(self, winners, hand_info, round_state): pass