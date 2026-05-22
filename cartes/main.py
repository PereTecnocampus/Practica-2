import random
import copy
import numpy as np
import os
from collections import namedtuple, Counter

BRONZE = 1
SILVER = 2
GOLD   = 3

CARD_NAMES = {BRONZE: "🥉", SILVER: "🥈", GOLD: "🥇"}

FULL_DECK = [BRONZE] * 6 + [SILVER] * 3 + [GOLD] * 1

HUMAN   = "Human"
MACHINE = "Machine"


CardGameState = namedtuple(
    "CardGameState",
    [
        "to_move",      # str: 'HUMAN' or 'MACHINE'
        "decks",        # {player: list}  top = index 0
        "revealed",     # {player: int|None}  currently flipped card
        "reserved",     # {player: int|None}  stored card
        "released",     # {player: tuple}     released cards (sorted)
        "blocked",      # {player: bool}      skip next turn?
            "blocked_series",   # {player: bool}      blocked once in current series?
        "utility",      # int: 0 ongoing, +1 Human wins, -1 Machine wins
    ]
)


def _other(player):
    return MACHINE if player == HUMAN else HUMAN


def _can_release(card, released_tuple):
    rel = list(released_tuple)
    if card == BRONZE:
        return True
    if card == SILVER:
        return rel.count(BRONZE) == 6
    if card == GOLD:
        return rel.count(BRONZE) == 6 and rel.count(SILVER) == 3
    return False


def _compute_utility(released):
    if GOLD in released[HUMAN]:
        return +1
    if GOLD in released[MACHINE]:
        return -1
    return 0


def _make_initial_state():
    def shuffled():
        d = list(FULL_DECK)
        random.shuffle(d)
        return d

    return CardGameState(
        to_move=HUMAN,
        decks={HUMAN: shuffled(), MACHINE: shuffled()},
        revealed={HUMAN: None, MACHINE: None},
        reserved={HUMAN: None, MACHINE: None},
        released={HUMAN: (), MACHINE: ()},
        blocked={HUMAN: False, MACHINE: False},
        blocked_series={HUMAN: False, MACHINE: False},
        utility=0,
    )


def _auto_flip(state):
    p = state.to_move
    if state.revealed[p] is not None or not state.decks[p]:
        return state
    decks    = {**state.decks,    p: state.decks[p][1:]}
    revealed = {**state.revealed, p: state.decks[p][0]}
    return state._replace(decks=decks, revealed=revealed)


class RingCardGame:

    def __init__(self, seed=None):
        if seed is not None:
            random.seed(seed)
        self.initial = _auto_flip(_make_initial_state())

    def to_move(self, state):
        return state.to_move

    def terminal_test(self, state):
        return state.utility != 0

    def utility(self, state, player):
        """
        Funció d'utilitat:
          +1: Humà guanya
          -1: Màquina guanya
        """
        return state.utility if player == HUMAN else -state.utility

    def actions(self, state):
        p   = state.to_move
        rev = state.revealed[p]
        res = state.reserved[p]
        rel = state.released[p]
        acts = []

        if rev is not None and _can_release(rev, rel):
            acts.append("release_revealed")

        if rev is not None and res is None:
            acts.append("reserve")

        if rev is not None:
            acts.append("return_revealed")

        if res is not None and _can_release(res, rel):
            acts.append("release_reserved")

        if res is not None:
            acts.append("return_reserved")

        if not state.blocked_series[p]:
            acts.append("block_opponent")

        if not acts:
            acts.append("pass")

        return acts

    # ------------------------------------------------------------------
    def result(self, state, action):
        p   = state.to_move
        opp = _other(p)

        decks     = {k: list(v) for k, v in state.decks.items()}
        revealed  = dict(state.revealed)
        reserved  = dict(state.reserved)
        released  = {k: list(v) for k, v in state.released.items()}
        blocked        = dict(state.blocked)
        blocked_series = dict(state.blocked_series)

        if action == "release_revealed":
            released[p].append(revealed[p])
            released[p].sort()
            revealed[p] = None

        elif action == "reserve":
            reserved[p] = revealed[p]
            revealed[p] = None

        elif action == "release_reserved":
            released[p].append(reserved[p])
            released[p].sort()
            reserved[p] = None

        elif action == "return_revealed":
            decks[p].append(revealed[p])
            random.shuffle(decks[p])
            revealed[p] = None

        elif action == "return_reserved":
            decks[p].append(reserved[p])
            random.shuffle(decks[p])
            reserved[p] = None

        elif action == "block_opponent":
            if revealed[p] is not None:
                decks[p].append(revealed[p])
                random.shuffle(decks[p])
                revealed[p] = None
            blocked[opp] = True
            blocked_series[p] = True

        util = _compute_utility(released)

        # Determine next active player
        if blocked[opp]:
            next_player = p
            blocked[opp] = False
        else:
            next_player = opp

        if next_player == opp:
            blocked_series[p] = False

        new_state = CardGameState(
            to_move=next_player,
            decks=decks,
            revealed=revealed,
            reserved=reserved,
            released={k: tuple(v) for k, v in released.items()},
            blocked=blocked,
            blocked_series=blocked_series,
            utility=util,
        )

        return _auto_flip(new_state)

    @staticmethod
    def _heuristic(state, player):
        opp   = _other(player)
        rel_p = list(state.released[player])
        rel_o = list(state.released[opp])
        score = (
            rel_p.count(BRONZE) * 10 +
            rel_p.count(SILVER) * 30 +
            (100 if GOLD in rel_p else 0) -
            rel_o.count(BRONZE) * 5 -
            rel_o.count(SILVER) * 15 -
            (50 if GOLD in rel_o else 0) +
            (5 if state.reserved[player] is not None else 0) -
            (3 if state.reserved[opp]    is not None else 0)
        )
        return score

    def display(self, state):
        print(self._render(state))

    def _render(self, state):
        sep = "-" * 58
        lines = [sep]
        for pl in [HUMAN, MACHINE]:
            rel_raw  = [CARD_NAMES[c] for c in state.released[pl]]
            rel = dict(Counter(rel_raw))

            res  = CARD_NAMES[state.reserved[pl]] if state.reserved[pl] else "--"
            rev  = CARD_NAMES[state.revealed[pl]] if state.revealed[pl] else "--"
            deck = len(state.decks[pl])
            lines.append(f"  {pl:8s} Released: {rel}")
            lines.append(f"           Reserved: {res:15s}  Revealed: {rev}  Deck: {deck}")
        lines.append(f"  Active player: {state.to_move}")
        lines.append(sep)
        return "\n".join(lines)

def alpha_beta_search(state, game, max_depth=5):
    player = game.to_move(state)

    def eval_fn(s):
        if game.terminal_test(s):
            return game.utility(s, player)
        return RingCardGame._heuristic(s, player)

    def max_value(s, alpha, beta, depth):
        if game.terminal_test(s) or depth == 0:
            return eval_fn(s)
        v = -np.inf
        for a in game.actions(s):
            v = max(v, min_value(game.result(s, a), alpha, beta, depth - 1))
            if v >= beta:
                return v # Poda
            alpha = max(alpha, v)
        return v

    def min_value(s, alpha, beta, depth):
        if game.terminal_test(s) or depth == 0:
            return eval_fn(s)
        v = np.inf
        for a in game.actions(s):
            v = min(v, max_value(game.result(s, a), alpha, beta, depth - 1))
            if v <= alpha:
                return v  # Poda
            beta = min(beta, v)
        return v

    best_score  = -np.inf
    best_action = None
    beta        = np.inf

    for a in game.actions(state):
        v = min_value(game.result(state, a), best_score, beta, max_depth)
        if v > best_score:
            best_score  = v
            best_action = a

    return best_action


def machine_player(game, state):
    print("\n  [Machine thinking...]")
    action = alpha_beta_search(state, game, max_depth=5)
    print(f"  [Machine plays: {action}]")
    return action


def human_player(game, state):
    game.display(state)
    acts = game.actions(state)
    print("\nYour actions:")
    for i, a in enumerate(acts):
        print(f"  {i}  {a}")
    while True:
        try:
            idx = int(input("Choose (number): "))
            if 0 <= idx < len(acts):
                return acts[idx]
        except ValueError:
            pass
        except KeyboardInterrupt:
            os._exit(1)
        print("  Invalid, try again.")


def greedy_player(game, state):
    acts = game.actions(state)
    for a in ["release_revealed", "release_reserved"]:
        if a in acts:
            return a
    return random.choice(acts)


# ---------------------------------------------------------------------------
# Game loop
# ---------------------------------------------------------------------------
def play_game(game, players):
    state = game.initial
    turn  = 0
    while not game.terminal_test(state):
        turn += 1
        current = state.to_move
        print(f"\n{'-'*58}")
        print(f"  Turn {turn:3d}: {current}")
        action = players[current](game, state)
        state  = game.result(state, action)

    game.display(state)
    winner = HUMAN if state.utility == 1 else MACHINE
    print(f"\n  GAME OVER! {winner} wins after {turn} turns!\n")
    return winner

if __name__ == "__main__":
    import sys

    game = RingCardGame()

    players = {HUMAN: human_player, MACHINE: machine_player}
    play_game(game, players)