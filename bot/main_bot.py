from pypokerengine.players import BasePokerPlayer
from bot.config.constants import DEBUG_MODE, DEBUG_ACTION
from bot.core.state_parser import parse_state
from bot.strategy.preflop.classifier import detect_preflop_situation
from bot.strategy.preflop.decision import get_preflop_action


class WorldClassBot(BasePokerPlayer):

    def declare_action(self, valid_actions, hole_card, round_state):

        # Convert engine chaos into clean state object
        state = parse_state(round_state, hole_card, self.uuid, valid_actions)

        if state.street == "preflop":
            situation = detect_preflop_situation(state)
            if DEBUG_MODE:
                print(f"Preflop Situation: {situation.value}")

        # For now, simple placeholder decision logic
        if state.street == "preflop":
            action, amount = get_preflop_action(state, valid_actions)
        else:
            action, amount = self._basic_decision(valid_actions, state)
    
        if DEBUG_MODE and DEBUG_ACTION:
            print(f"[BOT ACTION] {action} {amount}")

        return action, amount
    
    # -----------------------------
    # TEMPORARY DECISION LOGIC
    # -----------------------------
    def _basic_decision(self, valid_actions, state):

        action_names = [a["action"] for a in valid_actions]

        # find call amount safely
        call_action = next(a for a in valid_actions if a["action"] == "call")
        to_call = call_action["amount"]

        # -------------------------
        # CASE 1 — we can check
        # -------------------------
        if to_call == 0:
            return "call", 0   # this is CHECK

        # -------------------------
        # CASE 2 — preflop cheap call
        # -------------------------
        if state.street == "preflop" and to_call <= state.big_blind:
            return "call", to_call

        # -------------------------
        # CASE 3 — fold if possible
        # -------------------------
        if "fold" in action_names:
            return "fold", 0

        # -------------------------
        # CASE 4 — forced call
        # -------------------------
        return "call", to_call


    # -----------------------------
    # REQUIRED ENGINE METHODS
    # -----------------------------
    def receive_game_start_message(self, game_info): pass
    def receive_round_start_message(self, round_count, hole_card, seats): pass
    def receive_street_start_message(self, street, round_state): pass
    def receive_game_update_message(self, action, round_state): pass
    def receive_round_result_message(self, winners, hand_info, round_state): pass
