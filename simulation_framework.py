import sys
import os
import csv
import statistics
import matplotlib.pyplot as plt
from datetime import datetime
from pypokerengine.api.game import setup_config, start_poker
from dumb_bot import DumbBot
from super_bot import SuperBot
from tournament_titan import TournamentTitan
from apex_predator import ApexPredator
from smart_bot import SmartPokerBot
from bot.main_bot import WorldClassBot
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ======================================================
# CONFIGURATION
# ======================================================

NUM_SIMULATIONS = 10
ROUNDS_PER_GAME = 100
INITIAL_STACK = 1000
SMALL_BLIND = 10
TARGET_BOT = "World_Class_Bot"
LOG_DIR = "simulation_logs"

# ======================================================
# TEE LOGGER
# ======================================================

class Tee:
    def __init__(self, *files):
        self.files = files

    def write(self, data):
        for f in self.files:
            try:
                f.write(data)
            except UnicodeEncodeError:
                f.write(data.encode("utf-8", errors="ignore").decode("utf-8"))
            f.flush()

    def flush(self):
        for f in self.files:
            f.flush()

# ======================================================
# STATS COLLECTOR
# ======================================================

class StatsCollector:

    def __init__(self):
        self.results = []

        # Basic actions
        self.total_raises = 0
        self.total_calls = 0
        self.total_folds = 0
        self.total_actions = 0

        # Preflop stats
        self.vpip = 0
        self.pfr = 0
        self.three_bet = 0
        self.faced_three_bet = 0
        self.fold_to_three_bet = 0

        # Postflop stats
        self.flop_cbet = 0
        self.flop_opportunity = 0
        self.turn_barrel = 0
        self.turn_opportunity = 0
        self.river_aggression = 0
        self.river_opportunity = 0

        # Showdown
        self.showdowns = 0
        self.showdown_wins = 0

        # Hand counter
        self.total_hands = 0

    # --------------------------------------------------

    def add_game_result(self, profit):
        self.results.append(profit)

    # --------------------------------------------------

    def parse_actions_from_log(self, log_path):

        street = "preflop"
        hero_raised_preflop = False
        preflop_raises = 0

        with open(log_path, "r") as f:
            for line in f:

                # Detect new hand
                if "Started the round" in line:
                    self.total_hands += 1
                    street = "preflop"
                    hero_raised_preflop = False
                    preflop_raises = 0

                # Detect street transitions
                if 'Street "flop"' in line:
                    street = "flop"
                elif 'Street "turn"' in line:
                    street = "turn"
                elif 'Street "river"' in line:
                    street = "river"

                # Track raises count preflop
                if street == "preflop" and "declared \"raise" in line:
                    preflop_raises += 1

                # Target bot actions
                if TARGET_BOT in line:

                    if "declared \"raise" in line:
                        self.total_raises += 1
                        self.total_actions += 1

                        if street == "preflop":
                            self.pfr += 1
                            hero_raised_preflop = True

                            if preflop_raises > 1:
                                self.three_bet += 1

                        if street == "flop" and hero_raised_preflop:
                            self.flop_cbet += 1

                        if street == "turn":
                            self.turn_barrel += 1

                        if street == "river":
                            self.river_aggression += 1

                    elif "declared \"call" in line:
                        self.total_calls += 1
                        self.total_actions += 1

                        if street == "preflop":
                            self.vpip += 1

                    elif "declared \"fold" in line:
                        self.total_folds += 1
                        self.total_actions += 1

                        if street == "preflop" and preflop_raises > 1:
                            self.fold_to_three_bet += 1

                # Showdown detection
                if "won the round" in line:
                    if TARGET_BOT in line:
                        self.showdowns += 1
                        self.showdown_wins += 1
                    else:
                        self.showdowns += 1

        # Opportunities
        self.flop_opportunity += self.total_hands
        self.turn_opportunity += self.total_hands
        self.river_opportunity += self.total_hands

    # --------------------------------------------------

    def print_summary(self):

        avg_profit = statistics.mean(self.results)
        std_dev = statistics.stdev(self.results) if len(self.results) > 1 else 0

        print("\n========== OVERALL PERFORMANCE ==========")
        print("Games Played:", len(self.results))
        print("Average Profit:", round(avg_profit, 2))
        print("Std Deviation:", round(std_dev, 2))

        print("\n========== ACTION FREQUENCY ==========")
        print("Raise %:", round(self.total_raises / self.total_actions * 100, 2))
        print("Call %:", round(self.total_calls / self.total_actions * 100, 2))
        print("Fold %:", round(self.total_folds / self.total_actions * 100, 2))

        print("\n========== PREFLOP STATS ==========")
        print("VPIP %:", round(self.vpip / self.total_hands * 100, 2))
        print("PFR %:", round(self.pfr / self.total_hands * 100, 2))
        print("3-Bet %:", round(self.three_bet / self.total_hands * 100, 2))
        print("Fold to 3-Bet %:",
              round(self.fold_to_three_bet / self.total_hands * 100, 2))

        print("\n========== POSTFLOP STATS ==========")
        print("Flop CBet %:",
              round(self.flop_cbet / self.flop_opportunity * 100, 2))
        print("Turn Barrel %:",
              round(self.turn_barrel / self.turn_opportunity * 100, 2))
        print("River Aggression %:",
              round(self.river_aggression / self.river_opportunity * 100, 2))

        print("\n========== SHOWDOWN ==========")
        if self.showdowns > 0:
            print("Showdown Win %:",
                  round(self.showdown_wins / self.showdowns * 100, 2))
        else:
            print("Showdown Win %: 0")

    # --------------------------------------------------

    def export_csv(self):
        with open("simulation_summary.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Game #", "Profit"])
            for i, r in enumerate(self.results):
                writer.writerow([i+1, r])

        print("Saved simulation_summary.csv")

# ======================================================
# SIMULATION RUNNER
# ======================================================

class SimulationRunner:

    def __init__(self):
        self.stats = StatsCollector()
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)

    def run_single_game(self, game_index):

        log_path = os.path.join(LOG_DIR, f"game_{game_index}.txt")

        original_stdout = sys.stdout
        log_file = open(log_path, "w", encoding="utf-8")
        sys.stdout = Tee(original_stdout, log_file)

        try:
            config = setup_config(
                max_round=ROUNDS_PER_GAME,
                initial_stack=INITIAL_STACK,
                small_blind_amount=SMALL_BLIND
            )

            config.register_player(name="Super_Bot", algorithm=SuperBot())
            config.register_player(name="Dumb_2", algorithm=DumbBot())
            config.register_player(name="Tournament_Titan", algorithm=TournamentTitan())
            config.register_player(name="Apex_Predator", algorithm=ApexPredator())
            config.register_player(name="Smart_Bot", algorithm=SmartPokerBot())
            config.register_player(name="World_Class_Bot", algorithm=WorldClassBot())

            print(f"\n========== STARTING GAME {game_index} ==========")
            result = start_poker(config, verbose=1)

            profit = 0
            for player in result["players"]:
                if player["name"] == TARGET_BOT:
                    profit = player["stack"] - INITIAL_STACK

            print(f"Game {game_index} Profit: {profit}")

        finally:
            sys.stdout = original_stdout
            log_file.close()

        self.stats.add_game_result(profit)
        self.stats.parse_actions_from_log(log_path)

    def run(self):

        for i in range(1, NUM_SIMULATIONS + 1):
            self.run_single_game(i)

        self.stats.print_summary()
        self.stats.export_csv()
        Visualizer.visualize(self.stats.results)

# ======================================================
# VISUALIZER
# ======================================================

class Visualizer:

    @staticmethod
    def visualize(results):

        plt.figure()
        plt.plot(results)
        plt.title("Profit Per Game")
        plt.show()

        plt.figure()
        plt.hist(results, bins=20)
        plt.title("Profit Distribution")
        plt.show()

        cumulative = []
        running = 0
        for r in results:
            running += r
            cumulative.append(running)

        plt.figure()
        plt.plot(cumulative)
        plt.title("Cumulative Profit Curve")
        plt.show()

# ======================================================
# ENTRY
# ======================================================

if __name__ == "__main__":
    runner = SimulationRunner()
    runner.run()