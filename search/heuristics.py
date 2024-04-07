from .core import PlayerColor, Coord, PlaceAction

BOARD_N = 11

# TODO: make more efficient heuristic/s
def goal_line_completion(board: dict[Coord, PlayerColor], goal_line: list[Coord]):
    """
    Calculate the completion of the goal line.
    """
    return sum(1 for coord in goal_line if coord not in board)

# distance from PlaceAction to closest goal_line coord
def distance_to_goal_line(board: dict[Coord, PlayerColor], goal_line: list[Coord], move: PlaceAction):
    """
    Calculate the distance from a move to the closest goal line coord.
    """
    return min(abs(move_coord.r - goal_coord.r) + abs(move_coord.c - goal_coord.c) for move_coord in move.coords if move_coord != None for goal_coord in goal_line)

def calculate_heuristic(board, goal_line, move):
    """
    Calculate the heuristic of a given move.
    """
    return goal_line_completion(board, goal_line)/4 + distance_to_goal_line(board, goal_line, move)/4