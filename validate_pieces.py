
def get_all_pieces():
    pieces = set()
    for size in ["B", "S"]:
        for color in ["D", "L"]:
            for weight in ["E", "F"]:
                for shape in ["C", "P"]:
                    pieces.add(size + color + weight + shape)
    return pieces

def print_pieces_status(state):

    board = state.get('board', [])
    pending = state.get('piece')
    
    # Track used pieces
    used_pieces = set()
    for piece in board:
        if piece is not None:
            used_pieces.add(piece)
    if pending:
        used_pieces.add(pending)
    
    # All possible pieces
    all_pieces = get_all_pieces()
    
    # Available pieces
    available_pieces = all_pieces - used_pieces
    
    print(f"=== QUARTO PIECES STATUS ===")
    print(f"Board size: {len(board)}")
    print(f"Placed pieces: {len(used_pieces)}")
    print(f"Available pieces: {len(available_pieces)}")
    print("\nUSED PIECES:")
    for piece in sorted(used_pieces):
        print(f"- {piece}")
    print("\nAVAILABLE PIECES:")
    for piece in sorted(available_pieces):
        print(f"- {piece}")
    
    return available_pieces

if __name__ == "__main__":
    # Test with an example state
    test_state = {
        "board": [None, "BDEC", None, "SDFP", None, None, None, None, 
                  None, "SLFC", None, None, "BLFP", "BLEC", None, None],
        "piece": "BLEP"
    }
    print_pieces_status(test_state)
