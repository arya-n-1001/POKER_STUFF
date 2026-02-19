from pypokerengine.api.game import setup_config, start_poker
from dumb_bot import DumbBot
from human_player import HumanPlayer
from math_bot import MathBot
from strategy_bot import StrategyBot
from human_player import HumanPlayer
from pro_bot import ProBot
from super_bot import SuperBot
from tournament_titan import TournamentTitan
from apex_predator import ApexPredator
from competition_bot import CompetitionBot
from smart_bot import SmartPokerBot
from bot.main_bot import WorldClassBot


config = setup_config(max_round=20, initial_stack=1000, small_blind_amount=10)

# One Smart Bot vs Two Dumb ones
# config.register_player(name="Math_Pro", algorithm=MathBot())
# config.register_player(name="Pro_Bot", algorithm=ProBot())
# config.register_player(name="Super_Bot", algorithm=SuperBot())
# config.register_player(name="Competition_Bot", algorithm=CompetitionBot())
# config.register_player(name="Me (Human)", algorithm=HumanPlayer())
config.register_player(name="Strategy_Bot", algorithm=StrategyBot())
config.register_player(name="Dumb_2", algorithm=DumbBot())
config.register_player(name="Tournament_Titan", algorithm=TournamentTitan())
config.register_player(name="Apex_Predator", algorithm=ApexPredator())
config.register_player(name="Smart_Bot", algorithm=SmartPokerBot())
config.register_player(name="World_Class_Bot", algorithm=WorldClassBot())

game_result = start_poker(config, verbose=1)

print("\n--- Final Results ---")
for player in game_result['players']:
    print(f"Player: {player['name']} | Stack: {player['stack']}")