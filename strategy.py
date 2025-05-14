import random
import re

# Helper functions for Quarto board evaluation

def same(L):
    """Checks if all pieces in a line share at least one common attribute."""
    if None in L or len(L) < 4: # Ensure line is full
        return False
    # Convert string representations to sets for intersection
    try:
        common = set(L[0])
        for e in L[1:]:
            if e is None: return False
            common &= set(e)
        return bool(common)
    except (TypeError, IndexError):
        # Handle cases where L might not contain valid piece strings
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
    """Get available pieces from the game state by checking what's not on the board."""
    board = state['board']
    pending = state.get('piece')
    
    # Get pieces that are already on the board or pending
    used_pieces = set()
    for piece in board:
        if piece is not None:
            used_pieces.add(piece)
    
    if pending:
        used_pieces.add(pending)
    
    # All possible pieces
    all_pieces = get_all_pieces()
    
    # Filter out used pieces
    available_pieces = list(all_pieces - used_pieces)
    
    # Debug output
    print(f"[DEBUG] Board has {len([p for p in board if p is not None])}/{len(board)} pieces placed")
    print(f"[DEBUG] Found {len(available_pieces)} available pieces")
    print(f"[DEBUG] Available pieces: {', '.join(sorted(available_pieces)[:5])}{'...' if len(available_pieces) > 5 else ''}")
    
    return available_pieces


# only match strings of the form [B|S][D|L][E|F][C|P]
VALID_PIECE = re.compile(r'^[BS][DL][EF][CP]$')

def gen_move(state):
    board   = state['board']
    pending = state.get('piece')

    # valid empty slots
    empties = [i for i, v in enumerate(board) if v is None]
    if pending is not None and not empties:
        raise Exception("No empty squares left")

    # compute and filter available pieces
    available = extract_available_pieces(state)
    available = [p for p in available if VALID_PIECE.match(p)]
    if not available and pending is None:
        raise Exception("No pieces to give on first move")

    # first move: give a random valid piece
    if pending is None:
        choice = random.choice(available)
        return {'pos': None, 'piece': choice}

    # subsequent: place pending on a random empty, then give a random valid piece
    pos = random.choice(empties)
    next_piece = random.choice(available) if available else None
    return {'pos': pos, 'piece': next_piece}