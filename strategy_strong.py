import random
import re

def same(L):
    if None in L or len(L) < 4:
        return False
    try:
        common = set(L[0])
        for e in L[1:]:
            if e is None: return False
            common &= set(e)
        return bool(common)
    except (TypeError, IndexError):
        return False

def get_lines(board):
    lines = []
    for i in range(4):
        lines.append(board[i*4:(i+1)*4])
    for j in range(4):
        lines.append([board[i] for i in range(j,16,4)])
    lines.append([board[i*5] for i in range(4)])
    lines.append([board[3 + i*3] for i in range(4)])
    return lines

def is_winning(board):
    for line in get_lines(board):
        if None not in line and len(line) == 4:
            if same(line):
                return True
    return False

def get_all_pieces():
    pieces = set()
    for size in ["B", "S"]:
        for color in ["D", "L"]:
            for weight in ["E", "F"]:
                for shape in ["C", "P"]:
                    pieces.add(size + color + weight + shape)
    return pieces

def extract_available_pieces(state):
    board = state['board']
    pending = state.get('piece')
    used_pieces = set()
    for piece in board:
        if piece is not None:
            used_pieces.add(piece)
    if pending:
        used_pieces.add(pending)
    all_pieces = get_all_pieces()
    available_pieces = list(all_pieces - used_pieces)
    return available_pieces

VALID_PIECE = re.compile(r'^[BS][DL][EF][CP]$')

def find_winning_move(board, empties, piece):
    for pos in empties:
        new_board = board[:]
        new_board[pos] = piece
        if is_winning(new_board):
            return pos
    return None

def find_losing_pieces(board, empties, available):
    losing = set()
    for piece in available:
        for pos in empties:
            new_board = board[:]
            new_board[pos] = piece
            if is_winning(new_board):
                losing.add(piece)
                break
    return losing

def find_safe_pieces(board, empties, available):
    losing = find_losing_pieces(board, empties, available)
    safe = [p for p in available if p not in losing]
    return safe if safe else available

def block_opponent_win(board, empties, available):
    # Simule chaque pièce possible pour l'adversaire, bloque si possible
    for pos in empties:
        for piece in available:
            new_board = board[:]
            new_board[pos] = piece
            if is_winning(new_board):
                return pos
    return None

def count_potential(board, empties, piece):
    # Nombre de lignes où piece pourrait compléter une ligne à 3
    score = 0
    for pos in empties:
        new_board = board[:]
        new_board[pos] = piece
        for line in get_lines(new_board):
            if line.count(None) == 1 and piece in line:
                pieces = [p for p in line if p]
                shared = set(pieces[0])
                for p in pieces[1:]:
                    shared &= set(p)
                score += len(shared)
    return score

def select_best_pos(board, empties, piece):
    # Privilégie centre, puis coin, puis max potentiel
    center = [5,6,9,10]
    corners = [0,3,12,15]
    for pos in center:
        if pos in empties:
            return pos
    for pos in corners:
        if pos in empties:
            return pos
    # Sinon, maximise le potentiel de lignes gagnantes
    best = max(empties, key=lambda pos: count_potential(board, [pos], piece))
    return best

def select_best_piece(board, empties, available):
    # Ne jamais donner une pièce qui fait gagner l'adversaire
    safe = find_safe_pieces(board, empties, available)
    # Privilégie la pièce qui laisse le moins de possibilités de victoire à l'adversaire
    min_risk = None
    min_count = float('inf')
    for piece in safe:
        risk = 0
        for pos in empties:
            new_board = board[:]
            new_board[pos] = piece
            if is_winning(new_board):
                risk += 1
        if risk < min_count:
            min_count = risk
            min_risk = piece
    return min_risk if min_risk else random.choice(safe)

def gen_move(state):
    board = state['board']
    pending = state.get('piece')
    empties = [i for i, v in enumerate(board) if v is None]
    available = extract_available_pieces(state)
    available = [p for p in available if VALID_PIECE.match(p)]
    if pending is not None and not empties:
        raise Exception("No empty squares left")
    if not available and pending is None:
        raise Exception("No pieces to give on first move")

    # Premier coup : donne une pièce sûre
    if pending is None:
        safe = find_safe_pieces(board, empties, available)
        return {'pos': None, 'piece': random.choice(safe)}

    # 1. Gagner immédiatement
    win_pos = find_winning_move(board, empties, pending)
    if win_pos is not None:
        safe = find_safe_pieces(board, [i for i in empties if i != win_pos], available)
        return {'pos': win_pos, 'piece': random.choice(safe)}

    # 2. Bloquer la victoire adverse
    block_pos = block_opponent_win(board, empties, available)
    if block_pos is not None:
        safe = find_safe_pieces(board, [i for i in empties if i != block_pos], available)
        return {'pos': block_pos, 'piece': random.choice(safe)}

    # 3. Coup stratégique (centre, coin, max potentiel)
    pos = select_best_pos(board, empties, pending)
    next_empties = [i for i in empties if i != pos]
    piece = select_best_piece(board, next_empties, available)
    return {'pos': pos, 'piece': piece}
