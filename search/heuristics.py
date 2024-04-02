from .core import PlayerColor, Coord, PlaceAction, Direction

BOARD_N = 11

# TODO: make more efficient heuristic/s
# TODO: alter heuristic to cover multiple goal_list coords at once
def heuristic(a: Coord, b: Coord) -> int:
    """
    Calculate the Manhattan distance between two points.
    """
    return min(abs(a.r - b.r), BOARD_N - abs(a.r - b.r)) + min(abs(a.c - b.c), BOARD_N - abs(a.c - b.c))

def heuristic_to_goal(board: dict[Coord, PlayerColor], goal_line: list[Coord]) -> int:
    """
    Calculate the heuristic to the goal graph using Manhattan distance
    """
    sum = 0
    for coord in goal_line:
        closest = closest_to_point(board, coord)
        sum += heuristic(closest, coord)
    return sum

def heuristic_to_line(coord: Coord, goal_line: list[Coord]) -> int:
    """
    Calculate the heuristic to the goal line using Manhattan distance
    """
    distance = -1
    for goal in goal_line:
        if distance == -1:
            distance = heuristic(coord, goal)
        elif heuristic(coord, goal) < distance:
            distance = heuristic(coord, goal)
    return distance

def closest_to_point(board: dict[Coord, PlayerColor], point: Coord) -> Coord:
    """
    Find the closest coordinate to the goal line.
    """
    reds = [coord for coord in board if board.get(coord, None) == PlayerColor.RED]
    closest = reds[0]
    for coord in reds:
        if coord is None:
            continue
        if closest is None:
            closest = coord
        elif heuristic(coord, point) < heuristic(closest, point):
            closest = coord
    return closest