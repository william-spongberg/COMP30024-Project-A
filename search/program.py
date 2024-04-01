# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part A: Single Player Tetress

from .core import PlayerColor, Coord, PlaceAction, Direction
from .utils import render_board
import heapq

BOARD_N = 11


def search(board: dict[Coord, PlayerColor], goal: Coord) -> list[PlaceAction] | None:
    """
    This is the entry point for your submission. You should modify this
    function to solve the search problem discussed in the Part A specification.
    See `core.py` for information on the types being used here.

    Parameters:
        `board`: a dictionary representing the initial board state, mapping
            coordinates to "player colours". The keys are `Coord` instances,
            and the values are `PlayerColor` instances.
        `target`: the target BLUE coordinate to remove from the board.

    Returns:
        A list of "place actions" as PlaceAction instances, or `None` if no
        solution is possible.
    """

    # The render_board() function is handy for debugging. It will print out a
    # board state in a human-readable format. If your terminal supports ANSI
    # codes, set the `ansi` flag to True to print a colour-coded version!
    print(render_board(board, goal, ansi=True))

    # (your solution goes here)

    # scan board to find the start red positions
    start = []
    for coord, colour in board.items():
        if colour == PlayerColor.RED:
            start.append(coord)

    # if no start positions found, return None
    if start == None:
        return None

    # fill up with empty coords if less than 4
    if len(start) < 4:
        for _ in range(4 - len(start)):
            start.append(None)
    # convert to PlaceAction
    start = PlaceAction(*start)

    print("start:", start)
    # print("goal:", goal)

    # find the lines for the goal
    h_line = contruct_horizontal_line(goal, board)
    v_line = construct_vertical_line(goal, board)
    # temp get smaller line, change to heuristic later
    line = h_line if len(h_line) < len(v_line) else v_line

    print("goals:", line)

    path = a_star_search(board, start, line, goal)

    return path


# TODO: can optimise by recording valid adjacent moves in a dict
# TODO: alter heuristic to want to cover as many goal coords in one move as possible


def a_star_search(
    board: dict[Coord, PlayerColor],
    start_piece: PlaceAction,
    goal_line: list[Coord],
    goal: Coord,
) -> list[PlaceAction] | None:
    """
    Perform an A* search to find the shortest path from start to goal.
    """
    tetronimos = get_tetronimos()
    open_set = []
    came_from_coord: dict[Coord, Coord | None]
    came_from_piece: dict[Coord | None, PlaceAction]
    path = []
    pieces = []

    generated_nodes = 0
    expanded_nodes = 0
    duplicated_nodes = 0

    came_from_coord, came_from_piece, current_goal, g, f = init_a_star(
        start_piece, goal_line, open_set
    )

    while open_set:
        _, current_coord = heapq.heappop(
            open_set
        )  # node with lowest f_score is selected
        current_piece = came_from_piece[current_coord]
        expanded_nodes += 1

        # goal check first so current_goal can be updated for moving
        for coord in current_piece.coords:
            if coord == None:
                continue
            # can only be on goal if not actual target goal
            if coord == current_goal:
                # print board state
                board_temp = board.copy()
                print(
                    render_board(
                        perform_move(board_temp, current_piece), current_goal, ansi=True
                    )
                )
                # remove goal from goals
                goal_line.remove(coord)

                # print info
                print("REMOVED GOAL:", coord)
                print("GOALS:", goal_line)

                # put moves in board
                path, pieces = put_moves_in_board(
                    board, came_from_coord, came_from_piece, path, pieces, current_coord
                )

                # reset starting from current piece
                current_goal = find_closest_line_coord(coord, goal_line)
                
                # check if no goals remaining
                if not goal_line:
                    print("\nSOLUTION:")
                    print(render_board(board, goal, ansi=True))
                    return pieces[1:]

            # TODO: fix taking non-optimal path
            if coord in goal_line:
                # print board state
                board_temp = board.copy()
                print(
                    render_board(
                        perform_move(board_temp, current_piece), current_goal, ansi=True
                    )
                )
                print("REMOVED:", coord)
                goal_line.remove(coord)

                path, pieces = put_moves_in_board(
                    board, came_from_coord, came_from_piece, path, pieces, current_coord
                )

        # find next moves
        for coord in current_piece.coords:
            if coord == None:
                continue
            for adjacent_coord in get_valid_adjacents(board, coord):
                for move in get_valid_moves(
                    board,
                    tetronimos,
                    adjacent_coord,
                    reconstruct_pieces(
                        reconstruct_path(came_from_coord, current_coord),
                        came_from_piece,
                    ),
                ):
                    move_coord = find_closest_coord(move, current_goal)

                    if (
                        move not in came_from_piece
                        and move_coord not in came_from_coord
                    ):
                        generated_nodes += 1
                        came_from_coord[move_coord] = current_coord
                        came_from_piece[move_coord] = move
                        g[move_coord] = g[current_coord] + heuristic_to_line(
                            current_piece,
                            current_coord,
                            move_coord,
                            came_from_coord,
                            goal_line,
                        )
                        f[move_coord] = g[move_coord] + heuristic_to_line(
                            move, move_coord, current_goal, came_from_coord, goal_line
                        )
                        heapq.heappush(open_set, (f[move_coord], move_coord))

                        print_info(
                            goal_line,
                            goal,
                            came_from_coord,
                            generated_nodes,
                            expanded_nodes,
                            duplicated_nodes,
                            current_goal,
                            current_coord,
                            current_piece,
                            move,
                            move_coord,
                        )
                    else:
                        duplicated_nodes += 1

    return None


def print_info(
    goal_line,
    goal,
    came_from_coord,
    generated_nodes,
    expanded_nodes,
    duplicated_nodes,
    current_goal,
    current_coord,
    current_piece,
    move,
    move_coord,
):
    print(
        "coord:",
        move_coord,
        "h:",
        heuristic_to_line(
            current_piece, current_coord, move_coord, came_from_coord, goal_line
        ),
        "+",
        heuristic_to_line(move, move_coord, goal, came_from_coord, goal_line),
    )
    print("current goal:", current_goal)
    # print("goal line:", goal_line)
    # print_nodes(generated_nodes, expanded_nodes, duplicated_nodes)


def print_nodes(generated_nodes, expanded_nodes, duplicated_nodes):
    print("generated nodes:", generated_nodes)
    print("expanded nodes:", expanded_nodes)
    print("duplicate nodes:", duplicated_nodes)


def put_moves_in_board(
    board, came_from_coord, came_from_piece, path, pieces, current_coord
):
    path += reconstruct_path(came_from_coord, current_coord)
    path = list(dict.fromkeys(path))
    pieces += reconstruct_pieces(path, came_from_piece)
    pieces = list(dict.fromkeys(pieces))
    for piece in pieces:
        perform_move(board, piece)
    return path, pieces


def init_a_star(start_piece, goal_line, open_set):
    start_coord, current_goal = find_closest_coords(start_piece, goal_line)
    heapq.heappush(open_set, (0, start_coord))  # heap is initialized with start node
    came_from_coord = {start_coord: None}
    came_from_piece = {start_coord: start_piece}
    g = {start_coord: 0}
    f = {
        start_coord: heuristic_to_line(
            start_piece, start_coord, current_goal, came_from_coord, goal_line
        )
    }
    return came_from_coord, came_from_piece, current_goal, g, f  # path not found


def get_valid_moves(
    board: dict[Coord, PlayerColor],
    tetronimos: list[PlaceAction],
    coord: Coord,
    prev_moves: list[PlaceAction],
) -> list[PlaceAction]:
    """
    Get valid PlaceActions from a given coordinate.
    """
    valid_moves = []
    board_temp = board.copy()
    # get all previous pieces, put on temp board
    for move in prev_moves:
        perform_move(board_temp, move)

    # for each piece, check if valid, if valid, add to list of possible moves
    for move in get_moves(coord, tetronimos):
        if is_valid(board_temp, move):
            valid_moves.append(move)

    # print(valid_moves)
    return valid_moves


def is_valid(board: dict[Coord, PlayerColor], piece: PlaceAction) -> bool:
    """
    Check if the piece can be placed on the board.
    """
    for coord in piece.coords:
        if board.get(coord, None):
            return False
    return True


def get_tetronimos() -> list[PlaceAction]:
    """
    Get all possible tetronimos.
    """
    tetronimos = [
        PlaceAction(Coord(0, 0), Coord(1, 0), Coord(2, 0), Coord(3, 0)),  # I (straight)
        PlaceAction(Coord(0, 0), Coord(1, 0), Coord(2, 0), Coord(1, 1)),  # T (T-shape)
        PlaceAction(Coord(0, 0), Coord(1, 0), Coord(1, 1), Coord(2, 1)),  # S (S-shape)
        PlaceAction(Coord(0, 0), Coord(0, 1), Coord(1, 1), Coord(2, 1)),  # J (J-shape)
        PlaceAction(Coord(0, 0), Coord(0, 1), Coord(1, 0), Coord(2, 0)),  # L (L-shape)
    ]

    # rotate each tetronimo 4 times
    rotated_tetronimos = []
    for tetronimo in tetronimos:
        for i in range(4):
            rotated_tetronimos.append(rotate(tetronimo, i))

    # add cube
    rotated_tetronimos.append(
        PlaceAction(Coord(0, 0), Coord(1, 0), Coord(0, 1), Coord(1, 1))
    )
    return rotated_tetronimos


def get_moves(coord: Coord, tetronimos: list[PlaceAction]) -> list[PlaceAction]:
    # get all possible tetronimo moves from a given coordinate
    list_of_moves = []
    for tetronimo in tetronimos:
        move = [coord + Coord(x, y) for x, y in list(tetronimo.coords)]
        move = PlaceAction(*move)
        list_of_moves.append(move)
    return list_of_moves


def rotate(tetronimo: PlaceAction, times: int) -> PlaceAction:
    """
    Rotate a tetronimo a certain number of times.
    """
    rotated = list(tetronimo.coords)
    for _ in range(times):
        # rotated = [Coord(-y, x) for x, y in rotated] # rotate 90 degrees clockwise (x, y) -> (-y, x)
        rotated = [(Coord(y, x) - Coord((2 * y) % BOARD_N, 0)) for x, y in rotated]
    rotated = PlaceAction(*rotated)
    return rotated


def get_valid_adjacents(board: dict[Coord, PlayerColor], coord: Coord) -> list[Coord]:
    """
    Get valid adjacent coordinates from a given coordinate (empty adjacent coords).
    """
    valid_adjacents = []
    directions = [coord.up(), coord.down(), coord.left(), coord.right()]
    adjacents = [Coord(dir.r, dir.c) for dir in directions]
    for adjacent in adjacents:
        if not board.get(adjacent, None):
            valid_adjacents.append(adjacent)
    # print("valid:", valid_adjacents)
    return valid_adjacents


def get_invalid_adjacents(board: dict[Coord, PlayerColor], coord: Coord) -> list[Coord]:
    """
    Get invalid adjacent coordinates from a given coordinate (adjacent coords filled by pieces).
    """
    invalid_adjacents = []
    directions = [coord.up(), coord.down(), coord.left(), coord.right()]
    adjacents = [Coord(dir.r, dir.c) for dir in directions]
    for adjacent in adjacents:
        if board.get(adjacent, None):
            invalid_adjacents.append(adjacent)
    # print("invalid:", invalid_adjacents)
    return invalid_adjacents


def find_closest_line_coord(coord: Coord, line: list[Coord]) -> Coord | None:
    """
    Find the closest coordinate on a line from a given coordinate.
    """
    closest = None
    for line_coord in line:
        if closest == None:
            closest = line_coord
        elif heuristic(coord, line_coord) < heuristic(coord, closest):
            closest = line_coord
    return closest


def find_closest_coords(piece: PlaceAction, line: list[Coord]) -> tuple[Coord, Coord]:
    """
    Find the closest coordinates between a piece and a line.
    """
    min_dist = None
    line_coord = None
    for piece_coord in list(piece.coords):
        if piece_coord == None:
            continue
        if min_dist == None:
            min_dist = heuristic(piece_coord, line[0])
        line_coord = find_closest_line_coord(piece_coord, line)
        if line_coord != None:
            if heuristic(piece_coord, line_coord) < min_dist:
                min_dist = heuristic(piece_coord, line_coord)
    # check if None
    if line_coord == None:
        line_coord = line[0]
    return piece_coord, line_coord


def find_closest_coord(piece: PlaceAction, goal: Coord) -> Coord:
    """
    Find the closest coordinate to the goal from a piece.
    """
    closest = list(piece.coords)[0]
    for coord in list(piece.coords):
        if coord == None:
            continue
        if closest == None:
            closest = coord
        elif heuristic(coord, goal) < heuristic(closest, goal):
            closest = coord
    return closest


# TODO: make more efficient heuristic/s
def heuristic(a: Coord, b: Coord) -> int:
    """
    Calculate the Manhattan distance between two points.
    """
    return min(abs(a.r - b.r), BOARD_N - abs(a.r - b.r)) + min(
        abs(a.c - b.c), BOARD_N - abs(a.c - b.c)
    )


def heuristic_piece(
    piece: PlaceAction,
    coord: Coord,
    goal: Coord,
    came_from_coord: dict[Coord, Coord | None],
) -> int:
    """
    Calculate a heuristic for a piece based on the Manhattan distance to the goal and the number of pieces in the path so far.
    """
    manhattan_distance = sum(
        [heuristic(coord, goal) for coord in piece.coords if coord != None]
    )
    return manhattan_distance + count_pieces(came_from_coord, coord)


def heuristic_to_line(
    piece: PlaceAction,
    coord: Coord,
    goal: Coord,
    came_from_coord: dict[Coord, Coord | None],
    line: list[Coord],
) -> int:
    """
    Calculate a heuristic for a piece based on the maximum Manhattan distance to the goal and the number of pieces in the path and goal line.
    """
    closest_coord, closest_line_coord = find_closest_coords(piece, line)
    closest_manhattan_distance = heuristic(closest_coord, closest_line_coord)

    manhattan_distance = sum(
        [heuristic(coord, goal) for coord in piece.coords if coord != None]
    )
    for line_coord in line:
        if (
            sum(
                [
                    heuristic(coord, line_coord)
                    for coord in piece.coords
                    if coord != None
                ]
            )
            > manhattan_distance
        ):
            manhattan_distance = sum(
                [
                    heuristic(coord, line_coord)
                    for coord in piece.coords
                    if coord != None
                ]
            )

    return (
        count_pieces(came_from_coord, coord) + len(line) + closest_manhattan_distance
    )  # + manhattan_distance


def count_pieces(
    came_from_coord: dict[Coord, Coord | None], coord: Coord | None
) -> int:
    """
    Count the number of pieces in the path to the current node.
    """
    pieces = 0
    while coord in came_from_coord:
        coord = came_from_coord[coord]
        pieces += 1
    return pieces


def contruct_horizontal_line(
    coord: Coord, board: dict[Coord, PlayerColor]
) -> list[Coord]:
    """
    Construct a horizontal line for a coord.
    """
    line = []
    for i in range(BOARD_N):
        if not board.get(Coord(coord.r, i), None):
            line.append(Coord(coord.r, i))
    return line


def construct_vertical_line(
    coord: Coord, board: dict[Coord, PlayerColor]
) -> list[Coord]:
    """
    Construct a vertical line for a coord.
    """
    line = []
    for i in range(BOARD_N):
        if not board.get(Coord(i, coord.c), None):
            line.append(Coord(i, coord.c))
    return line


def reconstruct_path(
    came_from: dict[Coord, Coord | None], current: Coord | None
) -> list[Coord | None]:
    """
    Reconstruct the path from the start to the current node.
    """
    total_path = [current]
    while current in came_from:
        current = came_from[current]
        total_path.append(current)
    return total_path[::-1]


def reconstruct_pieces(
    coords: list[Coord | None], came_from_piece: dict[Coord | None, PlaceAction]
) -> list[PlaceAction]:
    """
    Reconstruct pieces used for path
    """
    pieces = []
    for coord in coords:
        if coord != None:
            piece = came_from_piece[coord]
            pieces.append(piece)
    return pieces


def perform_move(
    board: dict[Coord, PlayerColor], move: PlaceAction
) -> dict[Coord, PlayerColor]:
    """
    Perform a list of PlaceActions on the board.
    """
    if not is_valid(board, move):
        print("ERROR: move is invalid", move.coords)
        return board
    for coord in move.coords:
        board[coord] = PlayerColor.RED
    return board


# check all 19 possible moves, check if valid, if valid, add to list of possible moves
# for each possible move, calculate the cost of the move
# edge cost calculated from furthest coord of current to closest coord of next
# need to create some data structure to represent a piece (4 coords)

# add each coord to piece seperately, using add method (overridden in Coord class)

# find path to goal, then fill in? then back track, filling in first?

"""
# adjacent goal checking
for adjacent_coord in get_invalid_adjacents(board, coord):
    if (adjacent_coord == current_goal):
        pieces = reconstruct_pieces(reconstruct_path(came_from_coord, current_coord), came_from_piece)
        # print solution
        for piece in pieces:
            perform_move(board, piece)
        print("\nSOLUTION:")
        print(render_board(board, current_goal, ansi=True))
        print(goal_list)
        return pieces[1:]
"""