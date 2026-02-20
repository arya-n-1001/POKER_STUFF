def build_preflop_context(round_state, player_uuid):

    histories = round_state.get("action_histories", {})
    preflop_actions = histories.get("preflop", [])

    seats = round_state["seats"]
    dealer_btn = round_state["dealer_btn"]
    n = len(seats)

    bb = round_state["small_blind_amount"] * 2

    # --- build circular order ---
    order = [(dealer_btn + 1 + i) % n for i in range(n)]

    alive_order = [
        seats[i] for i in order
        if seats[i]["state"] == "participating"
    ]

    alive_uuids = {s["uuid"] for s in alive_order}

    hero_pos = next(i for i,s in enumerate(alive_order)
                    if s["uuid"] == player_uuid)

    # ---------------------------------------
    # --- analyze actions BEFORE decision ---
    # ---------------------------------------

    raises = 0
    callers = 0
    limpers = 0
    max_bet = bb

    last_raiser_uuid = None

    for action in preflop_actions:

        if action["uuid"] == player_uuid:
            continue

        act = action["action"].lower()
        amt = action.get("amount", 0)

        if act == "raise":
            raises += 1
            max_bet = max(max_bet, amt)

            # only track raiser if still alive
            if action["uuid"] in alive_uuids:
                last_raiser_uuid = action["uuid"]

        elif act == "call":
            if max_bet == bb:
                limpers += 1
            else:
                callers += 1

    # ---------------------------------------
    # --- compute players left to act ---
    # ---------------------------------------

    if last_raiser_uuid is None:
        # nobody raised OR all raisers folded
        players_left = len(alive_order) - hero_pos - 1

    else:
        raiser_pos = next(
            i for i,s in enumerate(alive_order)
            if s["uuid"] == last_raiser_uuid
        )

        if hero_pos < raiser_pos:
            players_left = raiser_pos - hero_pos - 1
        else:
            players_left = len(alive_order) - hero_pos - 1 + raiser_pos

    return {
        "raises_before": raises,
        "callers_before": callers,
        "limpers_before": limpers,
        "players_left_to_act": players_left,
        "is_closing_action": players_left == 0
    }
