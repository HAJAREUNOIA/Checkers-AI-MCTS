"""
evaluate.py  –  Évaluation automatique de l'IA MCTS (Checkers)
================================================================
Lance ce fichier depuis la racine de ton projet :
    python evaluate.py

Expérience unique : Win rate de l'IA forte vs IA faible
selon le nombre d'itérations MCTS.

Dépendances : matplotlib  (pip install matplotlib)
"""

import math
import random
import time
import csv
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# ──────────────────────────────────────────────────────────────
# Constantes
# ──────────────────────────────────────────────────────────────
RED_PIECE   = 1
BLACK_PIECE = 2
RED_KING    = 3
BLACK_KING  = 4

N = 8


# ──────────────────────────────────────────────────────────────
# Moteur de jeu (sans pygame)
# ──────────────────────────────────────────────────────────────

def create_board():
    board = [[0] * N for _ in range(N)]
    for r in range(N):
        for c in range(N):
            if (r + c) % 2 != 0:
                if r < 3:
                    board[r][c] = BLACK_PIECE
                elif r > 4:
                    board[r][c] = RED_PIECE
    return board


def opponent(turn):
    return BLACK_PIECE if turn == RED_PIECE else RED_PIECE


def in_bounds(r, c):
    return 0 <= r < N and 0 <= c < N


def get_available_moves(row, col, board, turn):
    piece = board[row][col]
    moves = []
    dirs = []
    if piece == BLACK_PIECE:
        dirs = [+1]
    elif piece == RED_PIECE:
        dirs = [-1]
    elif piece in (BLACK_KING, RED_KING):
        dirs = [+1, -1]

    opp = opponent(turn)
    for direction in dirs:
        for dc in (+1, -1):
            nr, nc = row + direction, col + dc
            if in_bounds(nr, nc) and board[nr][nc] == 0:
                moves.append((nr, nc))
            elif in_bounds(nr, nc) and board[nr][nc] in (opp, opp + 2):
                jr, jc = row + 2 * direction, col + 2 * dc
                if in_bounds(jr, jc) and board[jr][jc] == 0:
                    moves.append((jr, jc))
    return moves


def has_capture_moves(row, available_moves):
    return [(r, c) for (r, c) in available_moves if abs(r - row) == 2]


def get_all_possible_moves(board, turn):
    all_moves = {}
    capture_only = {}
    for r in range(N):
        for c in range(N):
            if board[r][c] == turn or board[r][c] == turn + 2:
                mvs = get_available_moves(r, c, board, turn)
                if mvs:
                    all_moves[(r, c)] = mvs
                caps = has_capture_moves(r, mvs)
                if caps:
                    capture_only[(r, c)] = caps
    return capture_only if capture_only else all_moves


# ──────────────────────────────────────────────────────────────
# CORRECTION 1 : make_move sans random.choice sur multi-capture
# On choisit la meilleure capture suivante via heuristique
# ──────────────────────────────────────────────────────────────
def make_move(board, move, piece_row, piece_col, prefer_turn=None):
    nb = [r[:] for r in board]
    pr, pc = piece_row, piece_col
    mr, mc = move
    nb[mr][mc] = nb[pr][pc]
    nb[pr][pc] = 0

    # Promotion
    if nb[mr][mc] == BLACK_PIECE and mr == N - 1:
        nb[mr][mc] = BLACK_KING
    elif nb[mr][mc] == RED_PIECE and mr == 0:
        nb[mr][mc] = RED_KING

    if abs(mr - pr) == 2:
        # Supprimer la pièce capturée
        nb[pr + (mr - pr) // 2][pc + (mc - pc) // 2] = 0

        # Déterminer le camp de la pièce qui vient de bouger
        piece_val = nb[mr][mc]
        turn_of_piece = piece_val if piece_val <= 2 else piece_val - 2

        next_mvs  = get_available_moves(mr, mc, nb, turn_of_piece)
        next_caps = has_capture_moves(mr, next_mvs)

        if next_caps:
            # CORRECTION : choisir la capture qui maximise le score heuristique
            # au lieu d'un random.choice — l'IA forte profite de ça
            best_cap = None
            best_score = -999
            for cap in next_caps:
                test_board = make_move(nb, cap, mr, mc, prefer_turn)
                score = _quick_score(test_board, turn_of_piece)
                if score > best_score:
                    best_score = score
                    best_cap = cap
            return make_move(nb, best_cap, mr, mc, prefer_turn)

    return nb


def _quick_score(board, turn):
    """Heuristique rapide pour choisir la meilleure multi-capture."""
    my_score = opp_score = 0
    opp = opponent(turn)
    for r in range(N):
        for c in range(N):
            p = board[r][c]
            if p == turn:
                my_score += 10
            elif p == turn + 2:
                my_score += 20
            elif p == opp:
                opp_score += 10
            elif p == opp + 2:
                opp_score += 20
    return my_score - opp_score


# ──────────────────────────────────────────────────────────────
# CORRECTION 2 : check_winner corrigé
# ──────────────────────────────────────────────────────────────
def check_winner(board, turn):
    red_has_moves = black_has_moves = False
    has_red = has_black = False
    for r in range(N):
        for c in range(N):
            p = board[r][c]
            if p in (RED_PIECE, RED_KING):
                has_red = True
                if not red_has_moves and get_available_moves(r, c, board, RED_PIECE):
                    red_has_moves = True
            elif p in (BLACK_PIECE, BLACK_KING):
                has_black = True
                if not black_has_moves and get_available_moves(r, c, board, BLACK_PIECE):
                    black_has_moves = True
    if not has_red or not has_black:
        return True
    if turn == RED_PIECE and not red_has_moves:
        return True
    if turn == BLACK_PIECE and not black_has_moves:
        return True
    return False


def get_winner_side(board, turn):
    """Retourne le camp gagnant ou None si partie non terminée."""
    has_red = has_black = False
    red_has_moves = black_has_moves = False
    for r in range(N):
        for c in range(N):
            p = board[r][c]
            if p in (RED_PIECE, RED_KING):
                has_red = True
                if not red_has_moves and get_available_moves(r, c, board, RED_PIECE):
                    red_has_moves = True
            elif p in (BLACK_PIECE, BLACK_KING):
                has_black = True
                if not black_has_moves and get_available_moves(r, c, board, BLACK_PIECE):
                    black_has_moves = True
    if not has_red:
        return BLACK_PIECE
    if not has_black:
        return RED_PIECE
    if turn == RED_PIECE and not red_has_moves:
        return BLACK_PIECE
    if turn == BLACK_PIECE and not black_has_moves:
        return RED_PIECE
    return None


# ──────────────────────────────────────────────────────────────
# MCTS
# ──────────────────────────────────────────────────────────────

class MCTSNode:
    __slots__ = ('board', 'turn', 'parent', 'move',
                 'children', 'wins', 'visits', 'untried_moves')

    def __init__(self, board, turn, parent=None, move=None):
        self.board = board
        self.turn  = turn
        self.parent = parent
        self.move   = move
        self.children = []
        self.wins   = 0.0
        self.visits = 0
        self.untried_moves = None

    def uct_value(self, c=1.41):
        if self.visits == 0:
            return float('inf')
        return (self.wins / self.visits) + c * math.sqrt(math.log(self.parent.visits) / self.visits)

    def best_child(self, c=1.41):
        return max(self.children, key=lambda ch: ch.uct_value(c))


# ──────────────────────────────────────────────────────────────
# CORRECTION 3 : evaluate_board améliorée — IA forte récompensée
# pour les pièces, les rois, la mobilité et le contrôle du centre
# ──────────────────────────────────────────────────────────────
def evaluate_board(board, mcts_player):
    red_score = black_score = 0
    for r in range(N):
        for c in range(N):
            p = board[r][c]
            if p == 0:
                continue
            center_bonus = 1.5 * (1.0 - abs(c - 3.5) / 3.5)
            row_bonus_r  = 3.0 * (7 - r) / 7.0   # RED avance vers r=0
            row_bonus_b  = 3.0 * r / 7.0          # BLACK avance vers r=7

            if p == RED_PIECE:
                red_score   += 10 + row_bonus_r + center_bonus
                # bonus défense arrière
                if r >= 5:
                    red_score += 0.5
            elif p == RED_KING:
                red_score   += 22 + center_bonus * 2
            elif p == BLACK_PIECE:
                black_score += 10 + row_bonus_b + center_bonus
                if r <= 2:
                    black_score += 0.5
            elif p == BLACK_KING:
                black_score += 22 + center_bonus * 2

    # Bonus mobilité (nombre de coups disponibles)
    red_moves   = sum(len(get_available_moves(r, c, board, RED_PIECE))
                      for r in range(N) for c in range(N)
                      if board[r][c] in (RED_PIECE, RED_KING))
    black_moves = sum(len(get_available_moves(r, c, board, BLACK_PIECE))
                      for r in range(N) for c in range(N)
                      if board[r][c] in (BLACK_PIECE, BLACK_KING))
    red_score   += red_moves   * 0.3
    black_score += black_moves * 0.3

    diff = red_score - black_score
    if mcts_player == BLACK_PIECE:
        diff = -diff
    return 1.0 / (1.0 + math.exp(-diff / 12.0))


# ──────────────────────────────────────────────────────────────
# Rollout intelligent pour l'IA forte
# ──────────────────────────────────────────────────────────────
def smart_random_move(moves, board, turn):
    """Priorité aux captures, puis aux coups agressifs vers le centre."""
    captures = [(p, m) for p, ms in moves.items() for m in ms if abs(m[0] - p[0]) == 2]
    if captures:
        # Choisir la capture qui prend le plus de valeur
        best = None
        best_val = -1
        for p, m in captures:
            captured_r = p[0] + (m[0] - p[0]) // 2
            captured_c = p[1] + (m[1] - p[1]) // 2
            val = 2 if board[captured_r][captured_c] in (RED_KING, BLACK_KING) else 1
            if val > best_val:
                best_val = val
                best = (p, m)
        return best

    scored = []
    center = 3.5
    for p, ms in moves.items():
        for m in ms:
            score = 0
            if turn == BLACK_PIECE:
                score += m[0] * 1.2
            elif turn == RED_PIECE:
                score += (7 - m[0]) * 1.2
            score += 2.0 - abs(m[1] - center) * 0.4
            if board[p[0]][p[1]] in (BLACK_KING, RED_KING):
                score += 2
            # Éviter les bords
            if m[1] in (0, 7):
                score -= 0.5
            scored.append((score, p, m))
    scored.sort(reverse=True)
    top = scored[:max(1, len(scored) // 3)]
    _, p, m = random.choice(top)
    return p, m


# ──────────────────────────────────────────────────────────────
# CORRECTION 4 : mcts_search avec backprop binaire (victoire/défaite)
# + rollout plus profond pour l'IA forte
# ──────────────────────────────────────────────────────────────
def mcts_search(board, mcts_player, iterations, is_strong=False):
    root = MCTSNode(board, mcts_player)
    all_moves = get_all_possible_moves(board, mcts_player)
    root.untried_moves = [(p, m) for p, mvs in all_moves.items() for m in mvs]

    # Profondeur de rollout plus grande pour l'IA forte
    max_depth = 120 if is_strong else 60

    for _ in range(iterations):
        node       = root
        temp_board = [r[:] for r in board]
        temp_turn  = mcts_player

        # ── Selection ────────────────────────────────────────
        while node.untried_moves == [] and node.children:
            node = node.best_child()
            if node.move:
                p, mv = node.move
                temp_board = make_move(temp_board, mv, p[0], p[1])
                temp_turn  = opponent(temp_turn)

        # ── Expansion ────────────────────────────────────────
        if node.untried_moves:
            chosen = random.choice(node.untried_moves)
            node.untried_moves.remove(chosen)
            p, mv = chosen
            temp_board = make_move(temp_board, mv, p[0], p[1])
            temp_turn  = opponent(temp_turn)
            child = MCTSNode(temp_board, temp_turn, parent=node, move=chosen)
            child_moves = get_all_possible_moves(temp_board, temp_turn)
            child.untried_moves = [(cp, cm) for cp, cms in child_moves.items() for cm in cms]
            node.children.append(child)
            node = child

        # ── Simulation (rollout) ─────────────────────────────
        sim_board = [r[:] for r in temp_board]
        sim_turn  = temp_turn
        depth = 0
        while depth < max_depth:
            if check_winner(sim_board, sim_turn):
                break
            sim_moves = get_all_possible_moves(sim_board, sim_turn)
            if not sim_moves:
                break
            p, mv = smart_random_move(sim_moves, sim_board, sim_turn)
            sim_board = make_move(sim_board, mv, p[0], p[1])
            sim_turn  = opponent(sim_turn)
            depth += 1

        # ── CORRECTION : backpropagation avec résultat binaire ──
        winner_side = get_winner_side(sim_board, sim_turn)
        if winner_side == mcts_player:
            result = 1.0
        elif winner_side is None:
            # Partie non terminée -> utiliser heuristique
            result = evaluate_board(sim_board, mcts_player)
        else:
            result = 0.0

        # ── Backpropagation ───────────────────────────────────
        cur = node
        while cur is not None:
            cur.visits += 1
            cur.wins   += result
            cur = cur.parent

    if not root.children:
        return None
    return max(root.children, key=lambda ch: ch.visits).move


# ──────────────────────────────────────────────────────────────
# Simulation d'une partie
# ──────────────────────────────────────────────────────────────
def play_one_game(iter_black, iter_red, max_moves=200,
                  black_is_strong=False, red_is_strong=False):
    board = create_board()
    turn  = RED_PIECE
    move_count = 0
    times_black = []
    times_red   = []

    while move_count < max_moves:
        if check_winner(board, turn):
            winner = opponent(turn)
            return winner, move_count, (
                sum(times_black)/len(times_black) if times_black else 0,
                sum(times_red)  /len(times_red)   if times_red   else 0
            )

        if turn == BLACK_PIECE:
            iters     = iter_black
            is_strong = black_is_strong
        else:
            iters     = iter_red
            is_strong = red_is_strong

        t0    = time.time()
        best  = mcts_search(board, turn, iters, is_strong=is_strong)
        elapsed = time.time() - t0

        if turn == BLACK_PIECE:
            times_black.append(elapsed)
        else:
            times_red.append(elapsed)

        if best is None:
            return opponent(turn), move_count, (
                sum(times_black)/len(times_black) if times_black else 0,
                sum(times_red)  /len(times_red)   if times_red   else 0
            )

        piece, mv = best
        board = make_move(board, mv, piece[0], piece[1])
        turn  = opponent(turn)
        move_count += 1

    return 'draw', move_count, (
        sum(times_black)/len(times_black) if times_black else 0,
        sum(times_red)  /len(times_red)   if times_red   else 0
    )


# ──────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────
REFERENCE_ITERS  = 1200          # itérations de l'IA forte (augmenté)
TEST_ITERS       = [100, 300, 600, 800]
GAMES_PER_CONFIG = 20            # 20 parties par config pour stats fiables


# ──────────────────────────────────────────────────────────────
# Expérience : Win rate vs itérations
# ──────────────────────────────────────────────────────────────

def run_experiment():
    print("\n" + "="*55)
    print("  EXPERIENCE : Taux de victoire vs itérations MCTS")
    print("="*55)
    results = []

    for it in TEST_ITERS:
        wins_forte = draws = 0
        total_time_forte = 0.0
        total_moves = 0
        moves_forte_list  = []
        moves_faible_list = []
        moves_draw_list   = []

        print(f"\n  IA_FORTE({REFERENCE_ITERS}) vs IA_FAIBLE({it})  "
              f"[{GAMES_PER_CONFIG} parties]")

        for g in range(GAMES_PER_CONFIG):
            if g % 2 == 0:
                # IA forte = BLACK
                winner, moves, (t_black, t_red) = play_one_game(
                    REFERENCE_ITERS, it,
                    black_is_strong=True, red_is_strong=False)
                won = (winner == BLACK_PIECE)
                total_time_forte += t_black
            else:
                # IA forte = RED
                winner, moves, (t_black, t_red) = play_one_game(
                    it, REFERENCE_ITERS,
                    black_is_strong=False, red_is_strong=True)
                won = (winner == RED_PIECE)
                total_time_forte += t_red

            if won:
                wins_forte += 1
                moves_forte_list.append(moves)
            elif winner == 'draw':
                draws += 1
                moves_draw_list.append(moves)
            else:
                moves_faible_list.append(moves)
            total_moves += moves

            label = 'FORTE' if won else ('NUL' if winner == 'draw' else 'FAIBLE')
            print(f"    Partie {g+1:2d}: {label}  ({moves} coups)", flush=True)

        winrate   = wins_forte / GAMES_PER_CONFIG * 100
        avg_time  = total_time_forte / GAMES_PER_CONFIG
        avg_moves = total_moves / GAMES_PER_CONFIG
        results.append({
            'it':           it,
            'winrate':      winrate,
            'avg_time':     avg_time,
            'avg_moves':    avg_moves,
            'draws':        draws,
            'wins_forte':   wins_forte,
            'wins_faible':  GAMES_PER_CONFIG - wins_forte - draws,
            'moves_forte':  moves_forte_list,
            'moves_faible': moves_faible_list,
            'moves_draw':   moves_draw_list,
        })

        print(f"  -> Win rate IA forte : {winrate:.0f}%  |  "
              f"Temps moy/coup : {avg_time:.2f}s  |  "
              f"Coups moy : {avg_moves:.1f}")

    return results


# ──────────────────────────────────────────────────────────────
# Graphe
# ──────────────────────────────────────────────────────────────

BLUE   = "#3266ad"
GREEN  = "#2a9d5c"
AMBER  = "#BA7517"
RED_C  = "#D85A30"
GRAY   = "#888780"
BG     = "#f9f9f7"
GRID   = "#e0ddd5"
LIGHT  = "#dce8f5"


def make_graph(results):
    iters     = [r['it']          for r in results]
    winrates  = [r['winrate']     for r in results]
    times     = [r['avg_time']    for r in results]
    avg_moves = [r['avg_moves']   for r in results]
    wins_f    = [r['wins_forte']  for r in results]
    wins_w    = [r['wins_faible'] for r in results]
    draws_n   = [r['draws']       for r in results]
    total     = GAMES_PER_CONFIG

    fig = plt.figure(figsize=(18, 11), facecolor=BG)
    gs  = fig.add_gridspec(2, 3, hspace=0.45, wspace=0.38,
                           left=0.06, right=0.97, top=0.88, bottom=0.08)

    ax_bar  = fig.add_subplot(gs[0, 0])
    ax_len  = fig.add_subplot(gs[0, 1])
    ax_line = fig.add_subplot(gs[0, 2])
    ax_tab  = fig.add_subplot(gs[1, 0:2])
    ax_box  = fig.add_subplot(gs[1, 2])

    for ax in [ax_bar, ax_len, ax_line, ax_tab, ax_box]:
        ax.set_facecolor(BG)

    # ── 1. Résultats du tournoi ───────────────────────────────
    total_wins_f = sum(wins_f)
    total_wins_w = sum(wins_w)
    total_draws  = sum(draws_n)
    grand_total  = total_wins_f + total_wins_w + total_draws

    categories = [f"IA Forte\n({REFERENCE_ITERS} itér.)", "IA Faible\n(variable)", "Match nul"]
    vals       = [total_wins_f, total_wins_w, total_draws]
    colors_bar = [BLUE, RED_C, GRAY]
    bars = ax_bar.bar(categories, vals, color=colors_bar, alpha=0.88,
                      width=0.5, zorder=3)
    for bar, v in zip(bars, vals):
        pct = v / grand_total * 100
        ax_bar.text(bar.get_x() + bar.get_width()/2,
                    v + grand_total * 0.02,
                    f"{v}\n({pct:.0f}%)",
                    ha='center', va='bottom', fontsize=9.5, fontweight='bold',
                    color=bar.get_facecolor())
    ax_bar.set_ylabel("Nombre de victoires", fontsize=10)
    ax_bar.set_title("Résultats du tournoi", fontsize=11, fontweight='bold')
    ax_bar.set_ylim(0, max(vals) * 1.35)
    ax_bar.grid(True, axis='y', color=GRID, linewidth=0.8, zorder=0)
    ax_bar.spines[['top', 'right']].set_visible(False)

    # ── 2. Longueur des parties ───────────────────────────────
    all_forte  = [m for r in results for m in r['moves_forte']]
    all_faible = [m for r in results for m in r['moves_faible']]
    all_draw   = [m for r in results for m in r['moves_draw']]

    bins = range(0, 210, 25)
    ax_len.hist(all_forte,  bins=bins, alpha=0.75, color=BLUE,  label="Forte gagne",  zorder=3)
    ax_len.hist(all_faible, bins=bins, alpha=0.75, color=RED_C, label="Faible gagne", zorder=3)
    ax_len.hist(all_draw,   bins=bins, alpha=0.60, color=GRAY,  label="Nul",          zorder=3)
    ax_len.set_xlabel("Nombre de coups", fontsize=10)
    ax_len.set_ylabel("Fréquence", fontsize=10)
    ax_len.set_title("Longueur des parties", fontsize=11, fontweight='bold')
    ax_len.legend(fontsize=8, framealpha=0.5)
    ax_len.grid(True, axis='y', color=GRID, linewidth=0.8, zorder=0)
    ax_len.spines[['top', 'right']].set_visible(False)

    # ── 3. Win rate vs itérations ─────────────────────────────
    ax_line.plot(iters, winrates, color=BLUE, linewidth=2.5, marker='o',
                 markersize=8, markerfacecolor='white',
                 markeredgecolor=BLUE, markeredgewidth=2,
                 label=f"IA Forte ({REFERENCE_ITERS} itér.)", zorder=4)
    faible_rates = [100 - w - (d/total*100) for w, d in zip(winrates, [r['draws']/total*100 for r in results])]
    ax_line.plot(iters, faible_rates, color=RED_C, linewidth=2, marker='s',
                 markersize=7, markerfacecolor='white',
                 markeredgecolor=RED_C, markeredgewidth=2,
                 linestyle='--', label="IA Faible", zorder=4)
    for x, y in zip(iters, winrates):
        ax_line.annotate(f"{y:.0f}%", (x, y),
                         textcoords="offset points", xytext=(0, 10),
                         ha='center', fontsize=8.5, color=BLUE, fontweight='bold')
    ax_line.axhline(80, color=GREEN, linewidth=1.5, linestyle='--', alpha=0.7, label="Cible 80%")
    ax_line.axhline(50, color=GRID,  linewidth=1.2, linestyle=':')
    ax_line.set_xlabel("Itérations MCTS (IA faible)", fontsize=10)
    ax_line.set_ylabel("Taux de victoire (%)", fontsize=10)
    ax_line.set_title("Victoire vs itérations", fontsize=11, fontweight='bold')
    ax_line.set_ylim(0, 110)
    ax_line.set_xticks(iters)
    ax_line.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax_line.legend(fontsize=8, framealpha=0.5)
    ax_line.grid(True, color=GRID, linewidth=0.8, zorder=0)
    ax_line.spines[['top', 'right']].set_visible(False)

    # ── 4. Tableau comparatif ─────────────────────────────────
    ax_tab.axis('off')
    col_labels = ["Config (itér. faible)", "Victoires Forte",
                  "Taux (%)", "Coups moy.", "Temps/coup (s)", "Nuls"]
    table_data = []
    for r in results:
        table_data.append([
            f"Forte({REFERENCE_ITERS}) vs Faible({r['it']})",
            f"{r['wins_forte']} / {total}",
            f"{r['winrate']:.0f}%",
            f"{r['avg_moves']:.1f}",
            f"{r['avg_time']:.2f}s",
            f"{r['draws']}",
        ])
    tbl = ax_tab.table(
        cellText=table_data,
        colLabels=col_labels,
        cellLoc='center', loc='center',
        bbox=[0, 0, 1, 1]
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9.5)
    for (row, col), cell in tbl.get_celld().items():
        cell.set_edgecolor(GRID)
        if row == 0:
            cell.set_facecolor(BLUE)
            cell.set_text_props(color='white', fontweight='bold')
        elif row % 2 == 0:
            cell.set_facecolor(LIGHT)
        else:
            cell.set_facecolor(BG)
    ax_tab.set_title("Tableau comparatif", fontsize=11,
                     fontweight='bold', pad=12)

    # ── 5. Variabilité ────────────────────────────────────────
    # Éviter le crash si une liste est vide
    box_data   = [all_forte  or [0],
                  all_faible or [0],
                  all_draw   or [0]]
    box_labels = ["Forte\ngagne", "Faible\ngagne", "Nul"]
    box_colors = [BLUE, RED_C, GRAY]
    bp = ax_box.boxplot(box_data, patch_artist=True,
                        medianprops=dict(color='white', linewidth=2),
                        whiskerprops=dict(linewidth=1.2),
                        capprops=dict(linewidth=1.2),
                        flierprops=dict(marker='o', markersize=4,
                                        markerfacecolor=AMBER, alpha=0.6))
    for patch, color in zip(bp['boxes'], box_colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.75)
    ax_box.set_xticklabels(box_labels, fontsize=9)
    ax_box.set_ylabel("Nombre de coups", fontsize=10)
    ax_box.set_title("Variabilité des parties", fontsize=11, fontweight='bold')
    ax_box.grid(True, axis='y', color=GRID, linewidth=0.8, zorder=0)
    ax_box.spines[['top', 'right']].set_visible(False)

    # ── Titre général ─────────────────────────────────────────
    total_games = len(TEST_ITERS) * GAMES_PER_CONFIG
    fig.suptitle(
        f"Évaluation de l'IA MCTS – Jeu de dames",
        fontsize=15, fontweight='bold', y=0.95
    )
    fig.text(0.5, 0.91,
             f"IA forte = {REFERENCE_ITERS} itér.  |  "
             f"{GAMES_PER_CONFIG} parties / config  |  "
             f"{total_games} parties au total",
             ha='center', fontsize=10, color=GRAY)

    out = "evaluation_ia_mcts.png"
    plt.savefig(out, dpi=150, bbox_inches='tight', facecolor=BG)
    print(f"\n  Graphe sauvegardé -> {out}")
    plt.close()


# ──────────────────────────────────────────────────────────────
# Export CSV
# ──────────────────────────────────────────────────────────────

def save_csv(results):
    with open("exp_winrate.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["iter_faible", "winrate_forte_%", "temps_moy_s",
                    "coups_moy", "nuls", "wins_forte", "wins_faible"])
        for r in results:
            w.writerow([r['it'], round(r['winrate'],1), round(r['avg_time'],3),
                        round(r['avg_moves'],1), r['draws'],
                        r['wins_forte'], r['wins_faible']])
    print("  CSV sauvegardé -> exp_winrate.csv")


# ──────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    total_games = len(TEST_ITERS) * GAMES_PER_CONFIG
    print("\n+==================================================+")
    print("|   Évaluation IA MCTS - Jeu de dames             |")
    print("+==================================================+")
    print(f"  Parties / config   : {GAMES_PER_CONFIG}")
    print(f"  Configs testées    : {TEST_ITERS}")
    print(f"  Total parties      : {total_games}")
    print(f"  IA de référence    : {REFERENCE_ITERS} itérations")

    results = run_experiment()

    print("\n  Génération du graphe...")
    make_graph(results)
    save_csv(results)

    print("\n  Résumé final :")
    print(f"  {'Itérations':<14} {'Win rate':<14} {'Temps/coup':<16} {'Coups moy'}")
    print("  " + "-"*54)
    for r in results:
        print(f"  {r['it']:<14} {r['winrate']:<14.0f}% {r['avg_time']:<16.2f}s {r['avg_moves']:.1f}")

    print("\n  Terminé ! Graphe -> evaluation_ia_mcts.png")
