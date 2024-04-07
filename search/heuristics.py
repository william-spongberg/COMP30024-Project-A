from .core import PlayerColor, Coord, PlaceAction

BOARD_N = 11

def goal_line_completion(board: dict[Coord, PlayerColor], goal_line: list[Coord]):
    """
    Calculate the completion of the goal line.
    """
    return sum(1 for coord in goal_line if coord not in board)

def distance_to_goal_line(board: dict[Coord, PlayerColor], goal_line: list[Coord], move: PlaceAction):
    """
    Calculate the distance from a move to the closest goal line coord.
    """
    return min(abs(move_coord.r - goal_coord.r) + abs(move_coord.c - goal_coord.c) for move_coord in move.coords if move_coord != None for goal_coord in goal_line)

def another_distance_to_goal_line(board: dict[Coord, PlayerColor], goal_line: list[Coord], move: PlaceAction):
    """
    Calculate the distance from a move to the closest goal line coord.
    """
    return min(abs(move_coord.r - goal_coord.r) + abs(move_coord.c - goal_coord.c) for move_coord in move.coords if move_coord != None for goal_coord in goal_line if goal_coord not in board)

def calculate_board_heuristic(board: dict[Coord, PlayerColor], goal: Coord) -> float:
    """
    Calculate the heuristic of a given move.
    """
    row_line = [Coord(goal.r, i) for i in range(BOARD_N)]
    col_line = [Coord(i, goal.c) for i in range(BOARD_N)]
    row_heuristic = goal_line_completion(board, row_line)/4
    col_heuristic = goal_line_completion(board, col_line)/4
    return min(row_heuristic, col_heuristic)

def calculate_heuristic(board: dict[Coord, PlayerColor], move: PlaceAction, goal: Coord) -> float:
    """
    Calculate the heuristic of a given move.
    """
    row_line = [Coord(goal.r, i) for i in range(BOARD_N)]
    col_line = [Coord(i, goal.c) for i in range(BOARD_N)]
    row_heuristic = goal_line_completion(board, row_line)/4 + another_distance_to_goal_line(board, row_line, move)/4
    col_heuristic = goal_line_completion(board, col_line)/4 + another_distance_to_goal_line(board, col_line, move)/4
    return min(row_heuristic, col_heuristic)