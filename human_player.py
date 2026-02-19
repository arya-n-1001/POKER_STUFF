from pypokerengine.players import BasePokerPlayer

class HumanPlayer(BasePokerPlayer):
    def declare_action(self, valid_actions, hole_card, round_state):
        print(f"\n--- YOUR TURN ---")
        print(f"Hole Card: {hole_card}")
        print(f"Community Card: {round_state['community_card']}")
        print(f"Main Pot: {round_state['pot']['main']['amount']}")
        
        # Display valid actions to the user
        print("Valid Actions:")
        for i, action in enumerate(valid_actions):
            print(f"{i}: {action['action']} (amount: {action['amount']})")

        # Get user input
        while True:
            try:
                choice = int(input("Select action index: "))
                if 0 <= choice < len(valid_actions):
                    action_item = valid_actions[choice]
                    action = action_item['action']
                    
                    # If raising, ask for the amount
                    if action == 'raise':
                        min_r = action_item['amount']['min']
                        max_r = action_item['amount']['max']
                        amount = int(input(f"Enter raise amount ({min_r} to {max_r}): "))
                        return action, amount
                    
                    return action, action_item['amount']
                else:
                    print("Invalid index. Try again.")
            except ValueError:
                print("Please enter a number.")

    def receive_game_start_message(self, game_info):
        print("Game Start!")

    def receive_round_start_message(self, round_count, hole_card, seats):
        print(f"\nRound {round_count} started. Your cards: {hole_card}")

    def receive_street_start_message(self, street, round_state):
        print(f"\nStreet: {street}")

    def receive_game_update_message(self, action, round_state):
        # This shows you what the bots just did
        print(f"Update: Player {action['player_uuid']} did {action['action']} (amount: {action['amount']})")

    def receive_round_result_message(self, winners, hand_info, round_state):
        print(f"\nRound Result: Winners: {[w['stack'] for w in winners]}")