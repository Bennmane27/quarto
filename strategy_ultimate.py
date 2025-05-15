import random
import re
import time
from collections import defaultdict

# -------------- CORE GAME FUNCTIONS --------------

def same(L):
    """Checks if all pieces in a line share at least one common attribute."""
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
    """Gets all rows, columns, and diagonals from the board."""
    lines = []
    # rows
    for i in range(4):
        lines.append(board[i*4:(i+1)*4])
    # columns
    for j in range(4):
        lines.append([board[i] for i in range(j,16,4)])
    # diagonals
    lines.append([board[i*5] for i in range(4)])  # 0,5,10,15
    lines.append([board[3 + i*3] for i in range(4)])  # 3,6,9,12
    return lines

def is_winning(board):
    """Checks if the current board state is a winning state."""
    for line in get_lines(board):
        if None not in line and len(line) == 4:
            if same(line):
                return True
    return False

def get_all_pieces():
    """Get all possible Quarto pieces as strings."""
    pieces = set()
    for size in ["B", "S"]:
        for color in ["D", "L"]:
            for weight in ["E", "F"]:
                for shape in ["C", "P"]:
                    pieces.add(size + color + weight + shape)
    return pieces

def extract_available_pieces(state):
    """Get available pieces from the game state."""
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

# -------------- ADVANCED EVALUATION FUNCTIONS --------------

def count_potential_lines(board, empties):
    """
    Evaluate the board by counting potential winning lines.
    Returns a score based on how many attributes are common in 3-piece lines.
    """
    score = 0
    lines = get_lines(board)
    
    for line in lines:
        # Skip lines that are already full
        if None not in line:
            continue
        
        # Count None values
        none_count = line.count(None)
        
        # Only consider lines with 1 empty space
        if none_count != 1:
            continue
        
        # Get non-None pieces in this line
        pieces = [p for p in line if p is not None]
        
        # Check if these pieces share any attribute
        if pieces:
            # Find attributes shared by all pieces in this line
            shared = set(pieces[0])
            for p in pieces[1:]:
                shared &= set(p)
            
            # The more pieces share attributes, the higher the score
            score += len(shared) * (4 - none_count)
    
    return score

def evaluate_board(board, player_turn):
    """
    Advanced board evaluation function.
    Returns a score from the perspective of the current player.
    Higher is better for the player.
    """
    if is_winning(board):
        return 1000 if player_turn else -1000
    
    empties = [i for i, p in enumerate(board) if p is None]
    potential_score = count_potential_lines(board, empties)
    
    # Return positive score if player's turn, negative if opponent's
    return potential_score if player_turn else -potential_score

# -------------- TRANSPOSITION TABLE --------------

# Global transposition table to cache results
transposition_table = {}

def board_to_key(board, piece):
    """Convert board to a hashable key for transposition table."""
    return (tuple(board), piece)

def lookup_position(board, piece, depth):
    """Lookup a position in the transposition table."""
    key = board_to_key(board, piece)
    if key in transposition_table and transposition_table[key][0] >= depth:
        return transposition_table[key][1]
    return None

def store_position(board, piece, depth, value):
    """Store a position in the transposition table."""
    key = board_to_key(board, piece)
    transposition_table[key] = (depth, value)

# -------------- ADVANCED MINIMAX WITH ALPHA-BETA PRUNING --------------

def minimax_with_pruning(board, pending, available, depth, alpha, beta, player_turn, max_depth, start_time, max_time):
    """
    Minimax algorithm with alpha-beta pruning for deeper search.
    
    Args:
        board: Current board state
        pending: Currently pending piece to place
        available: List of available pieces
        depth: Current search depth
        alpha, beta: Alpha-beta pruning parameters
        player_turn: True if it's the AI's turn, False for opponent
        max_depth: Maximum depth to search
        start_time: Time when search started
        max_time: Maximum time allowed for search (in seconds)
    """
    # Check time limit
    if time.time() - start_time > max_time:
        # Time's up, return current best
        return None, None, 0
    
    # Check transposition table
    cached_value = lookup_position(board, pending, depth)
    if cached_value is not None:
        return None, None, cached_value
    
    # Check terminal nodes
    empties = [i for i, p in enumerate(board) if p is None]
    if not empties or depth == 0:
        value = evaluate_board(board, player_turn)
        return None, None, value
    
    if player_turn:  # Maximizing player
        best_score = float('-inf')
        best_pos = None
        best_piece = None
        
        # First check for immediate wins
        for pos in empties:
            new_board = board[:]
            new_board[pos] = pending
            if is_winning(new_board):
                # We found a winning move
                store_position(board, pending, depth, 1000)
                return pos, None, 1000
        
        # Otherwise, evaluate all moves
        for pos in empties:
            new_board = board[:]
            new_board[pos] = pending
            
            # For each piece we could give
            for piece in available:
                if piece == pending:
                    continue
                
                new_available = [p for p in available if p != pending and p != piece]
                
                # Recursive call with opponent's turn
                _, _, score = minimax_with_pruning(
                    new_board, piece, new_available, 
                    depth-1, alpha, beta, False, 
                    max_depth, start_time, max_time
                )
                
                # Time check after recursive call
                if time.time() - start_time > max_time:
                    # Time's up, return current best
                    return best_pos, best_piece, best_score
                
                if score > best_score:
                    best_score = score
                    best_pos = pos
                    best_piece = piece
                
                alpha = max(alpha, best_score)
                if alpha >= beta:
                    break  # Beta cutoff
            
            if alpha >= beta:
                break  # Beta cutoff
        
        store_position(board, pending, depth, best_score)
        return best_pos, best_piece, best_score
    
    else:  # Minimizing player (opponent)
        best_score = float('inf')
        best_pos = None
        best_piece = None
        
        # First check if opponent can win immediately
        for pos in empties:
            new_board = board[:]
            new_board[pos] = pending
            if is_winning(new_board):
                # Opponent has a winning move
                store_position(board, pending, depth, -1000)
                return pos, None, -1000
        
        # Otherwise, evaluate all moves
        for pos in empties:
            new_board = board[:]
            new_board[pos] = pending
            
            # For each piece opponent could give
            for piece in available:
                if piece == pending:
                    continue
                
                new_available = [p for p in available if p != pending and p != piece]
                
                # Recursive call with our turn
                _, _, score = minimax_with_pruning(
                    new_board, piece, new_available, 
                    depth-1, alpha, beta, True, 
                    max_depth, start_time, max_time
                )
                
                # Time check after recursive call
                if time.time() - start_time > max_time:
                    # Time's up, return current best
                    return best_pos, best_piece, best_score
                
                if score < best_score:
                    best_score = score
                    best_pos = pos
                    best_piece = piece
                
                beta = min(beta, best_score)
                if alpha >= beta:
                    break  # Alpha cutoff
            
            if alpha >= beta:
                break  # Alpha cutoff
        
        store_position(board, pending, depth, best_score)
        return best_pos, best_piece, best_score

# -------------- PATTERN RECOGNITION --------------

def get_dangerous_patterns(board):
    """Identify dangerous patterns on the board that could lead to winning lines."""
    patterns = []
    lines = get_lines(board)
    
    for line_idx, line in enumerate(lines):
        # Skip lines that are already full
        if None not in line:
            continue
        
        # Count None values
        none_count = line.count(None)
        
        # Lines with exactly 2 empty spaces are particularly interesting
        if none_count == 2:
            pieces = [p for p in line if p is not None]
            if len(pieces) >= 2:
                # Check if these pieces share attributes
                shared = set(pieces[0])
                for p in pieces[1:]:
                    shared &= set(p)
                
                if shared:  # There are common attributes
                    # This is a dangerous pattern - mark empty positions
                    empty_positions = [i for i, val in enumerate(line) if val is None]
                    # Determine which global positions these are based on line type
                    global_positions = []
                    if line_idx < 4:  # Row
                        row = line_idx
                        global_positions = [row*4 + pos for pos in empty_positions]
                    elif line_idx < 8:  # Column
                        col = line_idx - 4
                        global_positions = [col + 4*pos for pos in range(4) if line[pos] is None]
                    elif line_idx == 8:  # Diagonal 1
                        global_positions = [pos*5 for pos in range(4) if line[pos] is None]
                    else:  # Diagonal 2
                        global_positions = [3 + pos*3 for pos in range(4) if line[pos] is None]
                    
                    patterns.append((global_positions, list(shared)))
    
    return patterns

def find_dangerous_pieces(board, available, patterns):
    """Find pieces that would allow completing a dangerous pattern."""
    dangerous = []
    
    for pattern in patterns:
        positions, attributes = pattern
        # For each piece, check if it matches the attributes
        for piece in available:
            matches = True
            for attr in attributes:
                if attr not in piece:
                    matches = False
                    break
            if matches:
                dangerous.append(piece)
    
    return list(set(dangerous))

# -------------- HEURISTICS --------------

def find_winning_move(board, empties, piece):
    """Find a move that wins immediately."""
    for pos in empties:
        new_board = board[:]
        new_board[pos] = piece
        if is_winning(new_board):
            return pos
    return None

def find_losing_piece(board, empties, available):
    """Find pieces that would allow opponent to win immediately."""
    losing = []
    for piece in available:
        for pos in empties:
            new_board = board[:]
            new_board[pos] = piece
            if is_winning(new_board):
                losing.append(piece)
                break
    return losing

def find_safe_piece(board, empties, available):
    """Find pieces that don't allow opponent to win immediately."""
    losing = set(find_losing_piece(board, empties, available))
    safe = [p for p in available if p not in losing]
    return safe if safe else available

def can_force_win(board, empties, available, pending):
    """Find a move that forces opponent to give a losing piece."""
    for pos in empties:
        new_board = board[:]
        new_board[pos] = pending
        
        # Check if all pieces are losing for opponent
        new_empties = [i for i in empties if i != pos]
        available_pieces = [p for p in available if p != pending]
        
        all_losing = True
        for piece in available_pieces:
            winning_pos = find_winning_move(new_board, new_empties, piece)
            if winning_pos is None:
                all_losing = False
                break
        
        if all_losing and available_pieces:
            return pos
    
    return None

def select_strategic_position(board, empties):
    """Select a strategic position based on the current board state."""
    # Prefer center positions initially
    center = [5, 6, 9, 10]
    center_empties = [pos for pos in empties if pos in center]
    if center_empties:
        return random.choice(center_empties)
    
    # If center is not available, use corners
    corners = [0, 3, 12, 15]
    corner_empties = [pos for pos in empties if pos in corners]
    if corner_empties:
        return random.choice(corner_empties)
    
    # Otherwise, use any available position
    return random.choice(empties)

# -------------- TIME MANAGEMENT AND ITERATIVE DEEPENING --------------

def iterative_deepening_search(board, pending, available, empties, max_depth=8, time_limit=1.0):
    """
    Perform iterative deepening search to find best move and piece.
    Gradually increases search depth until time limit is reached.
    """
    start_time = time.time()
    best_pos = None
    best_piece = None
    
    # First check for immediate wins
    if pending:
        win_pos = find_winning_move(board, empties, pending)
        if win_pos is not None:
            # If we can win immediately, do it
            safe_pieces = find_safe_piece(board, [i for i in empties if i != win_pos], available)
            if safe_pieces:
                return win_pos, random.choice(safe_pieces)
            return win_pos, random.choice(available) if available else None
    
    # Then check for forced wins
    if pending:
        force_pos = can_force_win(board, empties, available, pending)
        if force_pos is not None:
            # We found a move that forces opponent into a losing position
            safe_pieces = find_safe_piece(board, [i for i in empties if i != force_pos], available)
            if safe_pieces:
                return force_pos, random.choice(safe_pieces)
            return force_pos, random.choice(available) if available else None
    
    # Adjust max_depth based on game state
    filled_positions = 16 - len(empties)
    if filled_positions >= 8:
        # Late game, we can search deeper
        max_depth = min(10, max_depth + 2)
    
    # Iterative deepening
    for depth in range(2, max_depth + 1, 2):
        # Skip deep search on early game
        if filled_positions < 4 and depth > 4:
            continue
            
        pos, piece, _ = minimax_with_pruning(
            board, pending, available, depth, 
            float('-inf'), float('inf'), True,
            depth, start_time, time_limit
        )
        
        # Check if we need to stop due to time limit
        if time.time() - start_time > time_limit:
            break
        
        # Update best move
        if pos is not None:
            best_pos = pos
            best_piece = piece
    
    # If minimax didn't find anything (due to time constraints or other issues)
    if best_pos is None and pending is not None:
        best_pos = select_strategic_position(board, empties)
    
    if best_piece is None and available:
        safe_pieces = find_safe_piece(board, [i for i in empties if i != best_pos], available)
        best_piece = random.choice(safe_pieces) if safe_pieces else random.choice(available)
    
    return best_pos, best_piece

# -------------- MAIN STRATEGY FUNCTION --------------

def gen_move(state):
    """
    Generate the best move for the current game state.
    This is the main function called by the game engine.
    """
    board = state['board']
    pending = state.get('piece')
    
    # Get empty positions
    empties = [i for i, v in enumerate(board) if v is None]
    if pending is not None and not empties:
        raise Exception("No empty squares left")
    
    # Get available pieces
    available = extract_available_pieces(state)
    available = [p for p in available if VALID_PIECE.match(p)]
    if not available and pending is None:
        raise Exception("No pieces to give on first move")
    
    # First move (just choosing a piece)
    if pending is None:
        # For the first move, try to select a good piece
        patterns = get_dangerous_patterns(board)
        dangerous_pieces = find_dangerous_pieces(board, available, patterns)
        
        # Avoid giving dangerous pieces if possible
        safe_pieces = [p for p in available if p not in dangerous_pieces]
        if safe_pieces:
            return {'pos': None, 'piece': random.choice(safe_pieces)}
        return {'pos': None, 'piece': random.choice(available)}
    
    # For subsequent moves
    time_limit = 0.5  # 500ms time limit for thinking
    if len(empties) <= 6:  # End game, we can think longer
        time_limit = 1.0
    
    pos, next_piece = iterative_deepening_search(
        board, pending, available, empties, 
        max_depth=8, time_limit=time_limit
    )
    
    return {'pos': pos, 'piece': next_piece}
