from .core import PlayerColor, Coord, PlaceAction

BOARD_N = 11

# TODO: make more efficient heuristic/s
def empty_space_around_coord(board: dict[Coord, PlayerColor], coord: Coord, count: int) -> int:
    """
    Count the number of empty spaces around a coordinate.
    """
    directions = [coord.up(), coord.down(), coord.left(), coord.right()]
    adjacents = [Coord(dir.r, dir.c) for dir in directions]
    for adjacent in adjacents:
        if not board.get(adjacent, None): # if adjacent is empty
            count += 1
            if (count >= 4):
                return count % 5
            count += empty_space_around_coord(board, adjacent, count)
            if (count >= 4):
                return count % 5
    return count % 5

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

def path_distance_to_goal_line(board: dict[Coord, PlayerColor], goal_line: list[Coord], path: list[PlaceAction]):
    """
    Calculate the distance from a path to the closest goal line coord.
    """
    return min(distance_to_goal_line(board, goal_line, move) for move in path)

def calculate_heuristic(board: dict[Coord, PlayerColor], goal_line: list[Coord], path: list[PlaceAction]):
    """
    Calculate the heuristic of a given move.
    """
    return goal_line_completion(board, goal_line)/4 + path_distance_to_goal_line(board, goal_line, path)/4