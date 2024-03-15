# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part A: Single Player Tetress

from .core import PlayerColor, Coord, PlaceAction, Direction
from .utils import render_board
import heapq


def search(board: dict[Coord, PlayerColor], target: Coord) -> list[PlaceAction] | None:
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
    print(render_board(board, target, ansi=False))

    # (your solution goes here)

    # scan board to find the start red positions
    start = []
    for coord, colour in board.items():
        if colour == PlayerColor.RED:
            start.append(coord)

    # if no start positions found, return None
    if start is None:
        return None
    
    # fill up with empty coords if less than 4
    if len(start) < 4:
        for _ in range(4 - len(start)):
            start.append(None)   
    # convert to PlaceAction
    start = PlaceAction(*start)     
    
    print("start: ", start)
    print("goal: ", target)

    # a_star_search
    path = a_star_search(board, start, target)
    print(path)
    
    # TESTING #
    """
    crds = PlaceAction(Coord(2, 5), Coord(2, 6), Coord(3, 6), Coord(3, 7))
    print(crds)
    crds_c = crds.coords
    print(crds_c)
    crds_l = list(crds_c)
    print(crds_l)
    print(crds_l[0])
    """

    # Here we're returning "hardcoded" actions as an example of the expected
    # output format. Of course, you should instead return the result of your
    # search algorithm. Remember: if no solution is possible for a given input,
    # return `None` instead of a list.
    return [
        PlaceAction(Coord(2, 5), Coord(2, 6), Coord(3, 6), Coord(3, 7)),
        PlaceAction(Coord(1, 8), Coord(2, 8), Coord(3, 8), Coord(4, 8)),
        PlaceAction(Coord(5, 8), Coord(6, 8), Coord(7, 8), Coord(8, 8)),
    ]


def a_star_search(
    board: dict[Coord, PlayerColor], start: PlaceAction, goal: Coord
) -> list[Coord] | None:
    """
    Perform an A* search to find the shortest path from start to goal.
    """    
    board_state = board
    open_set = []
    closest_coord = find_closest_coord(start, goal)

    heapq.heappush(open_set, (0, closest_coord))  # heap is initialized with start node
    came_from = {closest_coord: None}
    came_from_piece = {closest_coord: start}
    g_score = {closest_coord: 0}
    f_score = {closest_coord: heuristic(closest_coord, goal)}

    while open_set:
        _, current = heapq.heappop(open_set)  # node with lowest f_score is selected

        if current == goal:
            path = reconstruct_path(came_from, current)
            print(reconstruct_pieces(path, came_from_piece))
            return reconstruct_path(came_from, current)

        for adjacent_coord in get_valid_adjacents(board_state, current):
            for move in get_valid_moves(board_state, adjacent_coord):
                move_coord = find_closest_coord(move, goal)

                if move_coord not in came_from:  # potential issues here, closest coord in goal may overlap with other pieces - but list is not hashable (need different way to hash?) | actually maybe not a problem, as only need piece to reach certain coord (multiple ways to reach same coord)
                    came_from[move_coord] = current
                    came_from_piece[move_coord] = move
                    g_score[move_coord] = g_score[current]+ heuristic(current, move_coord)
                    f_score[move_coord] = g_score[move_coord] + heuristic(move_coord, goal)
                    heapq.heappush(open_set, (f_score[move_coord], move_coord))
                    #print(move_coord, f_score[move_coord])
    return None  # path not found


def get_valid_moves(board: dict[Coord, PlayerColor], coord: Coord) -> list[PlaceAction]:
    """
    Get valid PieceActions from a given coordinate.
    """
    valid_moves = []
    # for each piece, check if valid, if valid, add to list of possible moves
    for move in get_moves(coord):
        if is_valid(board, move):
            valid_moves.append(move)

    #print(valid_moves)
    return valid_moves


def is_valid(board: dict[Coord, PlayerColor], piece: PlaceAction) -> bool:
    """
    Check if the piece can be placed on the board.
    """
    
    for coord in list(piece.coords):
        try:
            if board[coord]:
                return False
        except:
            return True
    return True


def get_moves(coord: Coord) -> list[PlaceAction]:
    # TODO: move to top of search method, keep defined as global
    # define tetronimo shapes
    tetronimos = [
        PlaceAction(Coord(0, 0), Coord(1, 0), Coord(2, 0), Coord(3, 0)),  # I (straight)
        PlaceAction(Coord(0, 0), Coord(1, 0), Coord(2, 0), Coord(1, 1)),  # T (T-shape)
        PlaceAction(Coord(0, 0), Coord(1, 0), Coord(1, 1), Coord(2, 1)),  # S (S-shape)
        PlaceAction(Coord(2, 0), Coord(0, 1), Coord(1, 1), Coord(2, 1)),  # L (L-shape)
    ]

    # rotate each tetronimo 4 times
    rotated_tetronimos = []
    for tetronimo in tetronimos:
        for i in range(4):
            rotated_tetronimos.append(rotate(tetronimo, i))
    
    # add cube
    rotated_tetronimos.append(PlaceAction(Coord(0, 0), Coord(1, 0), Coord(0, 1), Coord(1, 1)))

    # get all possible tetronimo moves from a given coordinate
    list_of_moves = []
    for tetronimo in rotated_tetronimos:
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
        rotated = [(Coord(y, x) - Coord((2 * y) % 11, 0)) for x, y in rotated] # TODO: fix this arithmetic
    rotated = PlaceAction(*rotated)
    return rotated


def get_valid_adjacents(board: dict[Coord, PlayerColor], coord: Coord) -> list[Coord]:
    """
    Get valid adjacent coordinates from a given coordinate.
    """
    valid_adjacents = []
    for direction in [Direction.Up, Direction.Down, Direction.Left, Direction.Right]:
        adjacent = coord + direction
        if adjacent not in board:
            valid_adjacents.append(adjacent)
    #print(valid_adjacents)
    return valid_adjacents


def find_closest_coord(piece: PlaceAction, goal: Coord) -> Coord:
    """
    Find the closest coordinate to the goal from a list of coordinates.
    """
    closest = list(piece.coords)[2] # TODO: fix this
    for coord in list(piece.coords):
        if coord == None:
            continue
        if heuristic(coord, goal) < heuristic(closest, goal):
            closest = coord
    return closest


def heuristic(a: Coord, b: Coord) -> int:
    """
    Calculate the Manhattan distance between two points.
    """
    return abs(a.r - b.r) + abs(a.c - b.c)


def reconstruct_path(came_from, current: Coord) -> list[Coord]:
    """
    Reconstruct the path from the start to the current node.
    """
    total_path = [current]
    while current in came_from:
        current = came_from[current]
        total_path.append(current)
    return total_path[::-1]

def reconstruct_pieces(coords: list[Coord], came_from_piece: dict[Coord, PlaceAction]): #-> list[PlaceAction]:
    """
    Reconstruct pieces used for path
    """
    pieces = []
    for coord in coords:
        if coord != None:
            #print(coord)
            piece = came_from_piece[coord]
            print(piece)
            pieces.append(piece.coords)
    return pieces


# check all 19 possible moves, check if valid, if valid, add to list of possible moves
# for each possible move, calculate the cost of the move
# edge cost calculated from furthest coord of current to closest coord of next
# need to create some data structure to represent a piece (4 coords)

# add each coord to piece seperately, using add method (overridden in Coord class)

# find path to goal, then fill in? then back track, filling in first?