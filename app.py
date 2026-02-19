from flask import Flask, render_template_string, request, jsonify
import threading
import time
from pypokerengine.api.game import setup_config, start_poker
from pypokerengine.players import BasePokerPlayer
from strategy_bot import StrategyBot
from dumb_bot import DumbBot

app = Flask(__name__)

# --- THE BRIDGE ---
class GameState:
    def __init__(self):
        self.log = []
        self.current_round = {}
        self.user_action = None
        self.waiting_for_user = False
        self.game_over = False

game_state = GameState()

class WebHumanPlayer(BasePokerPlayer):
    def declare_action(self, valid_actions, hole_card, round_state):
        # Update global state so the website knows it's your turn
        game_state.current_round = {
            "hole_card": hole_card,
            "community_card": round_state['community_card'],
            "pot": round_state['pot']['main']['amount'],
            "valid_actions": valid_actions,
            "ask_user": True
        }
        game_state.waiting_for_user = True
        
        # Pause the engine and wait for the Flask route to set game_state.user_action
        while game_state.user_action is None:
            time.sleep(0.1)
        
        action, amount = game_state.user_action
        game_state.user_action = None
        game_state.waiting_for_user = False
        return action, amount

    def receive_game_update_message(self, action, round_state):
        msg = f"Player {action['player_uuid']} did {action['action']} ({action['amount']})"
        game_state.log.append(msg)

    def receive_round_start_message(self, round_count, hole_card, seats):
        game_state.log.append(f"--- Round {round_count} Started ---")
    
    # Boilerplate
    def receive_game_start_message(self, game_info): pass
    def receive_street_start_message(self, street, round_state): pass
    def receive_round_result_message(self, winners, hand_info, round_state): pass

# --- FLASK ROUTES ---

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Poker Bot Arena</title>
    <style>
        body { font-family: sans-serif; background: #2c3e50; color: white; text-align: center; }
        .table { background: #27ae60; border-radius: 100px; padding: 50px; margin: 20px auto; width: 60%; border: 10px solid #7f8c8d; }
        .card { background: white; color: black; padding: 10px; border-radius: 5px; margin: 5px; display: inline-block; font-weight: bold; }
        .log { background: #34495e; height: 200px; overflow-y: scroll; text-align: left; padding: 10px; width: 80%; margin: auto; }
        button { padding: 15px 30px; font-size: 18px; cursor: pointer; background: #e67e22; color: white; border: none; border-radius: 5px; margin: 5px; }
        button:hover { background: #d35400; }
    </style>
</head>
<body>
    <h1>Poker Bot Arena</h1>
    <div class="table">
        <h3>Community Cards</h3>
        <div id="community"></div>
        <hr>
        <h3>Your Hand</h3>
        <div id="hand"></div>
        <h3>Pot: <span id="pot">0</span></h3>
    </div>

    <div id="controls" style="display:none;">
        <button onclick="sendAction('fold')">Fold</button>
        <button onclick="sendAction('call')">Call/Check</button>
        <input type="number" id="raise_amt" placeholder="Raise Amount">
        <button onclick="sendAction('raise')">Raise</button>
    </div>

    <h4>Game Log</h4>
    <div class="log" id="log"></div>

    <script>
        function update() {
            fetch('/state').then(response => response.json()).then(data => {
                document.getElementById('log').innerHTML = data.log.join('<br>');
                if (data.ask_user) {
                    document.getElementById('controls').style.display = 'block';
                    document.getElementById('hand').innerHTML = data.hole_card.map(c => `<span class="card">${c}</span>`).join('');
                    document.getElementById('community').innerHTML = data.community_card.map(c => `<span class="card">${c}</span>`).join('');
                    document.getElementById('pot').innerText = data.pot;
                } else {
                    document.getElementById('controls').style.display = 'none';
                }
            });
        }

        function sendAction(action) {
            let amt = 0;
            if (action === 'raise') amt = document.getElementById('raise_amt').value;
            fetch('/action', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({action: action, amount: parseInt(amt)})
            });
        }

        setInterval(update, 1000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/state')
def get_state():
    return jsonify({
        "log": game_state.log[-10:], # Last 10 messages
        "ask_user": game_state.waiting_for_user,
        "hole_card": game_state.current_round.get("hole_card", []),
        "community_card": game_state.current_round.get("community_card", []),
        "pot": game_state.current_round.get("pot", 0)
    })

@app.route('/action', methods=['POST'])
def take_action():
    data = request.json
    # Find the call amount from valid actions if user clicks call
    # For simplicity in this MVP, we assume certain amounts
    game_state.user_action = (data['action'], data['amount'])
    return jsonify({"status": "ok"})

def run_poker():
    config = setup_config(max_round=50, initial_stack=1000, small_blind_amount=10)
    config.register_player(name="Human", algorithm=WebHumanPlayer())
    config.register_player(name="StrategyBot", algorithm=StrategyBot())
    config.register_player(name="DumbBot", algorithm=DumbBot())
    start_poker(config, verbose=1)

if __name__ == '__main__':
    # Start Poker in a background thread
    threading.Thread(target=run_poker, daemon=True).start()
    # Start Flask
    app.run(port=5000)