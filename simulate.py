from pypokerengine.api.game import setup_config, start_poker
from dumb_bot import DumbBot
from super_bot import SuperBot
from tournament_titan import TournamentTitan
from apex_predator import ApexPredator
from smart_bot import SmartPokerBot
from bot.main_bot import WorldClassBot

import matplotlib.pyplot as plt
import statistics

# ======================================================
# CONFIGURATION
# ======================================================

NUM_SIMULATIONS = 2       # Increase later (1000+)
ROUNDS_PER_GAME = 100
INITIAL_STACK = 1000
SMALL_BLIND = 10
TARGET_BOT_NAME = "World_Class_Bot"

# ======================================================
# SINGLE MATCH
# ======================================================

def run_single_match():

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

    game_result = start_poker(config, verbose=0)

    for player in game_result["players"]:
        if player["name"] == TARGET_BOT_NAME:
            return player["stack"] - INITIAL_STACK

    return 0

# ======================================================
# RUN SIMULATIONS
# ======================================================

def run_simulation():

    results = []

    print("Running simulations...")

    for i in range(NUM_SIMULATIONS):
        profit = run_single_match()
        results.append(profit)
        print(f"Game {i+1}/{NUM_SIMULATIONS} | Profit: {profit}")

    return results

# ======================================================
# VISUALIZATION
# ======================================================

def visualize(results):

    avg_profit = statistics.mean(results)
    median_profit = statistics.median(results)
    std_dev = statistics.stdev(results)

    print("\n========== PERFORMANCE SUMMARY ==========")
    print("Total Games:", len(results))
    print("Average Profit:", round(avg_profit, 2))
    print("Median Profit:", round(median_profit, 2))
    print("Std Deviation:", round(std_dev, 2))

    # 1️⃣ Profit per game
    plt.figure()
    plt.plot(results)
    plt.title("Profit Per Game")
    plt.xlabel("Game #")
    plt.ylabel("Profit")
    plt.show()

    # 2️⃣ Distribution
    plt.figure()
    plt.hist(results, bins=30)
    plt.title("Profit Distribution")
    plt.xlabel("Profit")
    plt.ylabel("Frequency")
    plt.show()

    # 3️⃣ Cumulative profit
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
    results = run_simulation()
    visualize(results)