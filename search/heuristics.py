from .core import PlayerColor, Coord, PlaceAction
from .lines import construct_horizontal_line, construct_vertical_line
from statistics import mean

BOARD_N = 11

# TODO: make more efficient heuristic/s


def goal_line_completion(board: dict[Coord, PlayerColor], goal_line: list[Coord]):
    """
    Calculate the completion of the goal line.
    """
    return sum(1 for coord in goal_line if board.get(coord, None) is None)


def coord_distance_to_goal_line(board: dict[Coord, PlayerColor], goal: Coord, coord: Coord):
    """
    Calculate the distance from a coord to the closest goal line coord.
    """
    row_line = construct_horizontal_line(goal, board)
    col_line = construct_vertical_line(goal, board)

    return min(
        min(
            abs(coord.r - goal_coord.r) + abs(coord.c - goal_coord.c)
            for goal_coord in row_line
        ),
        min(
            abs(coord.r - goal_coord.r) + abs(coord.c - goal_coord.c)
            for goal_coord in col_line
        ),
    )


def board_distance_to_goal_line(
    board: dict[Coord, PlayerColor], goal_line: list[Coord]
):
    """
    Calculate the distance of cloest point to the furthest goal line coord.
    """
    # return mean(mean(abs(coord.r - goal_coord.r) + abs(coord.c - goal_coord.c)
    #     for coord in board if board[coord] == PlayerColor.RED)
    #     for goal_coord in goal_line)
    # return mean(abs(coord.r - goal_coord.r) + abs(coord.c - goal_coord.c)
    #     for coord in board if board[coord] == PlayerColor.RED
    #     for goal_coord in goal_line)
    # return max(abs(coord.r - goal_coord.r) + abs(coord.c - goal_coord.c)
    #     for coord in board if board[coord] == PlayerColor.RED
    #     for goal_coord in goal_line if board.get(goal_coord, None) is None)
    return min(
        abs(coord.r - goal_coord.r) + abs(coord.c - goal_coord.c)
        for coord in board
        if board[coord] == PlayerColor.RED
        for goal_coord in goal_line
    )


def calculate_heuristic(
    board: dict[Coord, PlayerColor], goal: Coord, move: PlaceAction
):
    """
    Calculate the heuristic of a given move.
    """
    row_line = construct_horizontal_line(goal, board)
    col_line = construct_vertical_line(goal, board)
    row_heuristic = (
        goal_line_completion(board, row_line)
        + board_distance_to_goal_line(board, row_line)
        + path_distance_to_goal_line(board, row_line)
        + empty_around_by(board, row_line)
    )
    col_heuristic = (
        goal_line_completion(board, col_line)
        + board_distance_to_goal_line(board, col_line)
        + path_distance_to_goal_line(board, col_line)
        + empty_around_by(board, col_line)
    )
    return min(row_heuristic, col_heuristic)


# experimental heuristics


def no_horizontal_obstacles_in_the_way(
    board: dict[Coord, PlayerColor], move_coord: Coord, goal_coord: Coord
):
    """
    Check if there are any obstacles in the way of a horizontal move.
    """
    for c in range(
        min(move_coord.c, goal_coord.c) + 1, max(move_coord.c, goal_coord.c)
    ):
        if board.get(Coord(move_coord.r, c), None) is PlayerColor.BLUE:
            return False
    return True


def no_vertical_obstacles_in_the_way(
    board: dict[Coord, PlayerColor], move_coord: Coord, goal_coord: Coord
):
    """
    Check if there are any obstacles in the way of a vertical move.
    """
    for r in range(
        min(move_coord.r, goal_coord.r) + 1, max(move_coord.r, goal_coord.r)
    ):
        if board.get(Coord(r, move_coord.c), None) is not PlayerColor.BLUE:
            return False
    return True


def path_distance_to_goal_line(board: dict[Coord, PlayerColor], goal_line: list[Coord]):
    """
    Calculate the distance from a path to the closest goal line coord.
    """
    min_r = min(
        (
            abs(red.r - goal_coord.r)
            for red in board
            if board[red] == PlayerColor.RED
            for goal_coord in goal_line
            if no_horizontal_obstacles_in_the_way(board, red, goal_coord)
        ),
        default=float("inf"),
    )

    min_c = min(
        (
            abs(red.c - goal_coord.c)
            for red in board
            if board[red] == PlayerColor.RED
            for goal_coord in goal_line
            if no_vertical_obstacles_in_the_way(board, red, goal_coord)
        ),
        default=float("inf"),
    )
    return min(min_r, min_c)


def empty_around_by(board: dict[Coord, PlayerColor], goal_line: list[Coord]):
    """
    Check if there are any empty spaces around a coord.
    """
    for coord in goal_line:
        if all(
            board.get(Coord(*coord_d), None) == PlayerColor.BLUE
            for coord_d in [coord.up(), coord.down(), coord.left(), coord.right()]
        ):
            return 1
    return 0
