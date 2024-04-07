from .core import PlayerColor, Coord, PlaceAction

BOARD_N = 11

# TODO: make more efficient heuristic/s


def goal_line_completion(board: dict[Coord, PlayerColor], goal_line: list[Coord]):
    """
    Calculate the completion of the goal line.
    """
    return sum(1 for coord in goal_line if board.get(coord, None) is None)


def coord_distance_to_goal_line(goal_line: list[Coord], coord: Coord):
    """
    Calculate the distance from a coord to the closest goal line coord.
    """
    return min(
        abs(coord.r - goal_coord.r) + abs(coord.c - goal_coord.c)
        for goal_coord in goal_line
    )


def move_distance_to_goal_line(board: dict[Coord, PlayerColor], goal_line: list[Coord], move: PlaceAction):
    """
    Calculate the distance from a move to the closest goal line coord.
    """
    # check if obstacles in the way
    
    min_r = min(
        (abs(move_coord.r - goal_coord.r)
        for move_coord in move.coords
        if move_coord != None
        for goal_coord in goal_line
        if no_horizontal_obstacles_in_the_way(board, move_coord, goal_coord)),
        default=float('inf')
    )
    
    min_c = min(
        (abs(move_coord.c - goal_coord.c)
        for move_coord in move.coords
        if move_coord != None
        for goal_coord in goal_line
        if no_vertical_obstacles_in_the_way(board, move_coord, goal_coord)),
        default=float('inf')
    )
    
    return min(min_r, min_c)

def no_horizontal_obstacles_in_the_way(board: dict[Coord, PlayerColor], move_coord: Coord, goal_coord: Coord):
    """
    Check if there are any obstacles in the way of a horizontal move.
    """
    for c in range(min(move_coord.c, goal_coord.c) + 1, max(move_coord.c, goal_coord.c)):
        if board.get(Coord(move_coord.r, c), None) is not None:
            return False
    return True

def no_vertical_obstacles_in_the_way(board: dict[Coord, PlayerColor], move_coord: Coord, goal_coord: Coord):
    """
    Check if there are any obstacles in the way of a vertical move.
    """
    for r in range(min(move_coord.r, goal_coord.r) + 1, max(move_coord.r, goal_coord.r)):
        if board.get(Coord(r, move_coord.c), None) is not None:
            return False
    return True

def no_obstacles_in_the_way(board: dict[Coord, PlayerColor], move_coord: Coord, goal_coord: Coord):
    """
    Check if there are any obstacles in the way of a move and a goal coord.
    """
    if move_coord.r == goal_coord.r:
        # check if there are any obstacles in the way of a horizontal move
        for c in range(min(move_coord.c, goal_coord.c) + 1, max(move_coord.c, goal_coord.c)):
            if board.get(Coord(move_coord.r, c), None) is not None:
                return False
    else:
        # check if there are any obstacles in the way of a vertical move
        for r in range(min(move_coord.r, goal_coord.r) + 1, max(move_coord.r, goal_coord.r)):
            if board.get(Coord(r, move_coord.c), None) is not None:
                return False
    return True


def path_distance_to_goal_line(board: dict[Coord, PlayerColor], goal_line: list[Coord], path: list[PlaceAction]):
    """
    Calculate the distance from a path to the closest goal line coord.
    """
    return min(move_distance_to_goal_line(board, goal_line, move) for move in path)


def calculate_heuristic(
    board: dict[Coord, PlayerColor], goal_line: list[Coord], path: list[PlaceAction]
) -> int:
    """
    Calculate the heuristic of a given move.
    """
    return (
        goal_line_completion(board, goal_line)
        + path_distance_to_goal_line(board, goal_line, path)
        + path_continuity(path)
    ) # type: ignore


# experimental heuristics

def path_continuity(path: list[PlaceAction]):
    """
    Calculate the number of consecutive pieces in the path.
    """
    consecutive_pieces = 0
    for i in range(1, len(path)):
        # Convert sets to lists before accessing by index
        current_coords = list(path[i].coords)
        previous_coords = list(path[i - 1].coords)
        if (
            abs(current_coords[0].r - previous_coords[-1].r)
            + abs(current_coords[0].c - previous_coords[-1].c)
            == 1
        ):
            consecutive_pieces += 1
    return consecutive_pieces
