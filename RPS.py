# What beats the given move
BEAT = {"R": "P", "P": "S", "S": "R"}

QUINCY_CYCLE = ["R", "R", "P", "P", "S"]
_BOT_ORDER = ("q", "k", "m", "a")


def _abbey_init_order():
    return {
        "RR": 0,
        "RP": 0,
        "RS": 0,
        "PR": 0,
        "PP": 0,
        "PS": 0,
        "SR": 0,
        "SP": 0,
        "SS": 0,
    }


def _predict_abbey_next(my_moves):
    """Abbey's next play after we have played my_moves (completed rounds only)."""
    oh = []
    po = _abbey_init_order()

    for j in range(len(my_moves)):
        raw_prev = "" if j == 0 else my_moves[j - 1]
        prev = "R" if not raw_prev else raw_prev
        oh.append(prev)
        last_two = "".join(oh[-2:])
        if len(last_two) == 2:
            po[last_two] += 1
        potential_plays = [prev + "R", prev + "P", prev + "S"]
        sub_order = {k: po[k] for k in potential_plays if k in po}
        max(sub_order, key=sub_order.get)

    raw_next = "" if len(my_moves) == 0 else my_moves[-1]
    prev_next = "R" if not raw_next else raw_next
    oh.append(prev_next)
    last_two = "".join(oh[-2:])
    if len(last_two) == 2:
        po[last_two] += 1
    potential_plays = [prev_next + "R", prev_next + "P", prev_next + "S"]
    sub_order = {k: po[k] for k in potential_plays if k in po}
    prediction = max(sub_order, key=sub_order.get)[-1:]
    return BEAT[prediction]


def _predict_mrugesh_next(my_moves):
    hist = []
    for i in range(len(my_moves)):
        hist.append("" if i == 0 else my_moves[i - 1])
    if len(my_moves) == 0:
        hist.append("")
    else:
        hist.append(my_moves[-1])
    last_ten = hist[-10:]
    most_frequent = max(set(last_ten), key=last_ten.count)
    if most_frequent == "":
        most_frequent = "S"
    return BEAT[most_frequent]


def _predict_quincy_next(num_opponent_moves_seen):
    idx = (num_opponent_moves_seen + 1) % len(QUINCY_CYCLE)
    return QUINCY_CYCLE[idx]


def _predict_kris_next(my_moves):
    if not my_moves:
        return BEAT["R"]
    return BEAT[my_moves[-1]]


def _increment_model_scores(opp, my_moves):
    """Update running hit counts for the latest opponent move opp[-1] at index len(opp)-1."""
    if not hasattr(player, "_scores"):
        player._scores = {"q": 0, "k": 0, "m": 0, "a": 0}

    i = len(opp) - 1
    if i < 0:
        return

    actual = opp[i]
    if _predict_quincy_next(i) == actual:
        player._scores["q"] += 1
    if _predict_kris_next(my_moves[:i] if i > 0 else []) == actual:
        player._scores["k"] += 1
    if _predict_mrugesh_next(my_moves[:i]) == actual:
        player._scores["m"] += 1
    if _predict_abbey_next(my_moves[:i]) == actual:
        player._scores["a"] += 1


def player(prev_play, opponent_history=[]):
    if not hasattr(player, "_my"):
        player._my = []

    if prev_play == "" and len(opponent_history) > 0:
        opponent_history.clear()
        player._my.clear()
        player._scores = {"q": 0, "k": 0, "m": 0, "a": 0}

    if prev_play:
        opponent_history.append(prev_play)
        _increment_model_scores(opponent_history, player._my)

    my_moves = player._my
    n_opp = len(opponent_history)

    pred_q = _predict_quincy_next(n_opp)
    pred_k = _predict_kris_next(my_moves)
    pred_m = _predict_mrugesh_next(my_moves)
    pred_a = _predict_abbey_next(my_moves)

    if n_opp == 0:
        move = BEAT[pred_m]
    else:
        sc = player._scores
        bot = max(_BOT_ORDER, key=lambda b: (sc[b], -_BOT_ORDER.index(b)))
        move = BEAT[{"q": pred_q, "k": pred_k, "m": pred_m, "a": pred_a}[bot]]

    player._my.append(move)
    return move
