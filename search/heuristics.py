from .core import PlayerColor, Coord, PlaceAction

BOARD_N = 11

# TODO: make more efficient heuristic/s
def calculate_move_heuristic(board, goal_line, move: PlaceAction):
    """
    Calculate the heuristic of a given move.
    """
    total_distance = 0
    num_pieces = 0
    piece_length = 4 # max length of a piece
    temp_board = board.copy()
    # update immediately so that rest coords wont consider goal been filled in this move
    temp_board.update({coord: PlayerColor.RED for coord in move.coords})
    for coord in move.coords:
        if (coord not in goal_line and coord != None):
            # only check rest unfilled goal line, so that the move intends to approach rest space
            total_distance += sum(distance_between_coords(goal_coord, coord) for goal_coord in goal_line if goal_coord not in temp_board)
        num_pieces += 1
    return total_distance / (num_pieces * piece_length) if num_pieces else 0

def distance_between_coords(coord1, coord2):
    """
    Helper function to calculate the Manhattan distance between two coordinates. In case the BOARD_N is forgotten in calculation. 
    """
    row = min(abs(coord1.r - coord2.r), BOARD_N - abs(coord1.r - coord2.r))
    col = min(abs(coord1.c - coord2.c), BOARD_N - abs(coord1.c - coord2.c))
    return row + col

def goal_line_completion(board, goal_line):
    """
    Calculate the completion of the goal line.
    """
    return sum(1 for coord in goal_line if coord not in board)

def calculate_heuristic(board, goal_line, move):
    """
    Calculate the heuristic of a given move.
    """
    return calculate_move_heuristic(board, goal_line, move) + goal_line_completion(board, goal_line)
    