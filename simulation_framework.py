import sys
import os
import csv
import re
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

NUM_SIMULATIONS = 20
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
        self.action_counts = []
        self.total_raises = 0
        self.total_calls = 0
        self.total_folds = 0
        self.total_actions = 0

    def add_game_result(self, profit):
        self.results.append(profit)

    def parse_actions_from_log(self, log_path):
        raises = 0
        calls = 0
        folds = 0

        with open(log_path, "r") as f:
            for line in f:
                if TARGET_BOT in line:
                    if "raise" in line:
                        raises += 1
                    elif "call" in line:
                        calls += 1
                    elif "fold" in line:
                        folds += 1

        self.total_raises += raises
        self.total_calls += calls
        self.total_folds += folds
        self.total_actions += (raises + calls + folds)

        self.action_counts.append({
            "raises": raises,
            "calls": calls,
            "folds": folds
        })

    def print_summary(self):

        avg_profit = statistics.mean(self.results)
        std_dev = statistics.stdev(self.results) if len(self.results) > 1 else 0

        raise_pct = (self.total_raises / self.total_actions * 100) if self.total_actions else 0
        call_pct = (self.total_calls / self.total_actions * 100) if self.total_actions else 0
        fold_pct = (self.total_folds / self.total_actions * 100) if self.total_actions else 0

        print("\n========== OVERALL PERFORMANCE ==========")
        print("Games Played:", len(self.results))
        print("Average Profit:", round(avg_profit, 2))
        print("Std Deviation:", round(std_dev, 2))
        print("Total Raises:", self.total_raises)
        print("Total Calls:", self.total_calls)
        print("Total Folds:", self.total_folds)
        print("Raise %:", round(raise_pct, 2))
        print("Call %:", round(call_pct, 2))
        print("Fold %:", round(fold_pct, 2))

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

        # Profit per game
        plt.figure()
        plt.plot(results)
        plt.title("Profit Per Game")
        plt.xlabel("Game #")
        plt.ylabel("Profit")
        plt.show()

        # Distribution
        plt.figure()
        plt.hist(results, bins=30)
        plt.title("Profit Distribution")
        plt.xlabel("Profit")
        plt.ylabel("Frequency")
        plt.show()

        # Cumulative curve
        cumulative = []
        running = 0

        for r in results:
            running += r
            cumulative.append(running)

        plt.figure()
        plt.plot(cumulative)
        plt.title("Cumulative Profit Curve")
        plt.xlabel("Game #")
        plt.ylabel("Cumulative Profit")
        plt.show()

# ======================================================
# ENTRY
# ======================================================

if __name__ == "__main__":
    runner = SimulationRunner()
    runner.run()