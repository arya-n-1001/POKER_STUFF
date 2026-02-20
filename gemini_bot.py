import json
import time
from google import genai
from google.genai import types
from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate

GOOGLE_API_KEY = "AIzaSyDt7EOG5HEfm1-PeYLu93KaEWG0P-xwb-w"
class GeminiBot(BasePokerPlayer):
    def __init__(self):
        super().__init__()
        self.client = genai.Client(api_key=GOOGLE_API_KEY)
        self.model_id = "gemini-2.5-pro" 
        self.cooldown_until = 0
        
        # --- NEW: TRACKING STATS ---
        self.opponents = {} # Stores {uuid: {actions: [], name: str}}

    def receive_game_update_message(self, action, round_state):
        """Track every move made by opponents to build a profile."""
        p_uuid = action['player_uuid']
        if p_uuid == self.uuid: return
        
        if p_uuid not in self.opponents:
            # Find the name for this UUID
            name = next((p['name'] for p in round_state['seats'] if p['uuid'] == p_uuid), "Unknown")
            self.opponents[p_uuid] = {'name': name, 'raises': 0, 'calls': 0, 'total': 0}
        
        self.opponents[p_uuid]['total'] += 1
        if action['action'] == 'raise':
            self.opponents[p_uuid]['raises'] += 1
        elif action['action'] == 'call':
            self.opponents[p_uuid]['calls'] += 1

    def declare_action(self, valid_actions, hole_card, round_state):
        win_rate = estimate_hole_card_win_rate(
            nb_simulation=500,
            nb_player=len(round_state['seats']),
            hole_card=gen_cards(hole_card),
            community_card=gen_cards(round_state['community_card'])
        )

        # Build a "Scouting Report" for the LLM
        scouting_report = ""
        for p_uuid, stats in self.opponents.items():
            aggression = (stats['raises'] / stats['total']) * 100 if stats['total'] > 0 else 0
            scouting_report += f"- {stats['name']}: Aggression Score {aggression:.1f}% ({stats['total']} moves seen)\n"

        prompt = f"""
        You are a World-Class Poker Pro. 
        
        OPPONENT SCOUTING REPORT:
        {scouting_report}
        
        CURRENT STATE:
        - My Hole Cards: {hole_card}
        - Board: {round_state['community_card']}
        - Win Prob: {win_rate:.2f}
        - Valid Actions: {json.dumps(valid_actions)}
        
        STRATEGY ADVICE: 
        If an opponent has a high Aggression Score (>50%), they are likely bluffing or overplaying. 
        If it's low (<15%), they only raise with the nuts.
        
        Return JSON: {{"action": "fold/call/raise", "amount": int, "reasoning": "str"}}
        """

        try:
            if time.time() < self.cooldown_until: raise Exception("Cooldown")

            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            res_data = json.loads(response.text)
            print(f" [Gemini] Thinking: {res_data.get('reasoning')}")
            return self._validate_action(res_data.get("action", "fold"), int(res_data.get("amount", 0)), valid_actions)

        except Exception as e:
            if "429" in str(e): self.cooldown_until = time.time() + 60
            return self._math_fallback(valid_actions, win_rate)

    def _math_fallback(self, valid_actions, win_rate):
        call_amt = [a for a in valid_actions if a['action'] == 'call'][0]['amount']
        if win_rate > 0.4:
            r_info = [a for a in valid_actions if a['action'] == 'raise']
            if r_info: return 'raise', r_info[0]['amount']['min']
            return 'call', call_amt
        return ('call', 0) if call_amt == 0 else ('fold', 0)

    def _validate_action(self, action, amount, valid_actions):
        names = [a['action'] for a in valid_actions]
        if action not in names: action = 'fold'
        if action == 'raise':
            r = [a for a in valid_actions if a['action'] == 'raise'][0]
            amount = max(r['amount']['min'], min(r['amount']['max'], amount))
        elif action == 'call':
            amount = [a for a in valid_actions if a['action'] == 'call'][0]['amount']
        return action, amount

    # Boilerplate
    def receive_game_start_message(self, game_info): pass
    def receive_round_start_message(self, round_count, hole_card, seats): pass
    def receive_street_start_message(self, street, round_state): pass
    def receive_round_result_message(self, winners, hand_info, round_state): pass