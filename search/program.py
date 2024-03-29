# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part A: Single Player Tetress

from .core import PlayerColor, Coord, PlaceAction, Direction
from .utils import render_board
from typing import Optional
import heapq

BOARD_N = 11
NONE_PIECE = PlaceAction(Coord(0, 0), Coord(0, 0), Coord(0, 0), Coord(0, 0))

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
    #print("goal:", goal)

    # a_star_search
    #path = a_star_search(board, start, goal)
    #print(path)
    
    # change goal as needed? e.g. change to the closest row/col line
    # decide which row/col line is best -> most filled, closest to start
    
    # path find from coord to coord of line, saving path up to last piece in pieces variable
    # different goal-checking method now - not adjacent to goal, but on the line (coords)
    
    
    h_line = construct_horizontal_line(goal, board)
    v_line = construct_vertical_line(goal, board)
    
    path_h = a_star_search(board, start, h_line, goal)
    path_v = a_star_search(board, start, v_line, goal)
    
    if (path_h == None):
        return path_v
    if (path_v == None):
        return path_h
    else:
        return path_h if len(path_h) < len(path_v) else path_v
    
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
    """
    coord = Coord(0,5)
    up = coord.up()
    #down = coord.down()
    #left = coord.left()
    #right = coord.right()
    c = Coord(up.r, up.c)
    print(c)
    """

    # Here we're returning "hardcoded" actions as an example of the expected
    # output format. Of course, you should instead return the result of your
    # search algorithm. Remember: if no solution is possible for a given input,
    # return `None` instead of a list.
    """
    return [
        PlaceAction(Coord(2, 5), Coord(2, 6), Coord(3, 6), Coord(3, 7)),
        PlaceAction(Coord(1, 8), Coord(2, 8), Coord(3, 8), Coord(4, 8)),
        PlaceAction(Coord(5, 8), Coord(6, 8), Coord(7, 8), Coord(8, 8)),
    ]
    """
# TODO: can optimise by recording valid adjacent moves in a dict
# TODO: alter heuristic to want to cover as many goal coords in one move as possible

def a_star_search(board: dict[Coord, PlayerColor], start_piece: PlaceAction, goal_line: list[Coord], goal: Coord) -> list[PlaceAction] | None:
    """
    Perform an A* search to find the shortest path from start to goal.
    """
    tetronimos = get_tetronimos()
    open_set = []
    
    generated_nodes = 0
    expanded_nodes = 0
    duplicated_nodes = 0
    
    heapq.heappush(open_set, (0, 0, start_piece))  # heap is initialized with start node
    parent_move = {start_piece: NONE_PIECE} # parent of each move
    g = {start_piece: 0}
    f = {start_piece: heuristic_to_goal(get_current_board(board, start_piece, parent_move), goal_line)}

    while open_set:
        _, _, current_piece = heapq.heappop(open_set)  # node with lowest f_score is selected
        expanded_nodes += 1
        has_children = False
        current_board = get_current_board(board, current_piece, parent_move)
        # find next moves
        for coord in current_piece.coords:
            if coord == None:
                continue
            for adjacent_coord in get_valid_adjacents_all_over_the_board(current_board, goal_line):
                for move in get_valid_moves(current_board, tetronimos, adjacent_coord):
                    has_children = True
                    generated_nodes += 1
                    parent_move[move] = current_piece
                    new_board = get_current_board(current_board, move, parent_move)
                    if all([new_board.get(coord, None) for coord in goal_line]):
                        print(render_board(new_board, goal, ansi=True))
                        print("Success! Path found.")
                        print("length:", g[current_piece] + 1)
                        return reconstruct_pieces(parent_move, move)
                    g[move] = g[current_piece] + 1
                    f[move] = g[move] + heuristic_to_goal(new_board, goal_line)
                    heapq.heappush(open_set, (f[move], generated_nodes, move))
                    
                    print(render_board(new_board, goal, ansi=True))
                    print("move:", move, "g:", g[move], "f:", f[move])
                    print("goal:", goal)
                    print("goal line:", goal_line)
                    print("generated nodes:", generated_nodes)
                    print("expanded nodes:", expanded_nodes)
                    print("duplicate nodes:", duplicated_nodes)
                    # else:
                    #     duplicated_nodes += 1
        if not has_children:
            parent_move.pop(current_piece)
                        
    return None  # path not found

def get_valid_moves(board: dict[Coord, PlayerColor], tetronimos: list[PlaceAction], coord: Coord) -> list[PlaceAction]:
    """
    Get valid PlaceActions from a given coordinate.
    """
    valid_moves = []
    
    # for each piece, check if valid, if valid, add to list of possible moves
    for move in get_moves(coord, tetronimos):
        if is_valid(board, move):
            valid_moves.append(move)

    #print(valid_moves)
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
    rotated_tetronimos.append(PlaceAction(Coord(0, 0), Coord(1, 0), Coord(0, 1), Coord(1, 1)))
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

def get_valid_adjacents_all_over_the_board(board: dict[Coord, PlayerColor], goal_line: list[Coord]) -> list[Coord]:
    """
    Get valid adjacent coordinates from all over the board.
    """
    valid_adjacents = []
    for coord in board:
        if (coord is not None) and (board.get(coord, None) == PlayerColor.RED):
            directions = [coord.up(), coord.down(), coord.left(), coord.right()]
            adjacents = [Coord(dir.r, dir.c) for dir in directions]
            for adjacent in adjacents:
                if not board.get(adjacent, None): # if adjacent is empty
                    valid_adjacents.append(adjacent)
    # rearrage list to order by distance to goal list
    valid_adjacents.sort(key=lambda x: heuristic_to_line(x, goal_line))
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
    #print("invalid:", invalid_adjacents)
    return invalid_adjacents

def find_closest_coord(piece: PlaceAction, goal: Coord) -> Coord:
    """
    Find the closest coordinate to the goal from a piece.
    """
    closest = list(piece.coords)[0]
    for coord in list(piece.coords):
        if coord is None:
            continue
        if closest is None:
            closest = coord
        elif heuristic(coord, goal) < heuristic(closest, goal):
            closest = coord
    return closest



# TODO: make more efficient heuristic/s
# TODO: alter heuristic to cover multiple goal_list coords at once
def heuristic(a: Coord, b: Coord) -> int:
    """
    Calculate the Manhattan distance between two points.
    """
    ar = 0
    ac = 0
    if (a is not None):
        ar = a.r
        ac = a.c
    br = 0
    bc = 0
    if (b is not None):
        br = b.r
        bc = b.c
    # return min(abs(a.r - b.r), BOARD_N - abs(a.r - b.r)) + min(abs(a.c - b.c), BOARD_N - abs(a.c - b.c))
    ab = abs(ar - br) + abs(ac - bc)
    return pow(ab, 2)

def heuristic_to_goal(board: dict[Coord, PlayerColor], goal_line: list[Coord]) -> int:
    """
    Calculate the heuristic to the goal graph using Manhattan distance
    """
    sum = 0
    for coord in goal_line:
        closest = clostest_to_point(board, coord)
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

def clostest_to_point(board: dict[Coord, PlayerColor], point: Coord) -> Coord:
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

def get_current_board(base_board: dict[Coord, PlayerColor], piece: PlaceAction, parent_move: dict[PlaceAction, PlaceAction]) -> dict[Coord, PlayerColor]:
    """
    Get the current board state after placing a piece.
    """
    temp_board = base_board.copy()
    while piece in parent_move:
        for coord in piece.coords:
            # already filled, return
            if temp_board.get(coord, None):
                return temp_board
            # fill in the coord
            temp_board[coord] = PlayerColor.RED
        piece = parent_move[piece]
    return temp_board

def count_pieces(came_from: dict[Coord, Coord | None], coord: Coord | None) -> int:
    """
    Count the number of pieces in the path to the current node.
    """
    pieces = 0
    while (coord in came_from):
        coord = came_from[coord]
        pieces += 1
    return pieces

def construct_horizontal_line(coord: Coord, board: dict[Coord, PlayerColor]) -> list[Coord]:
    """
    Construct a horizontal line for a coord.
    """
    line = []
    for i in range(BOARD_N):
        if not board.get(Coord(coord.r, i), None):
            line.append(Coord(coord.r, i))
    return line

def construct_vertical_line(coord: Coord, board: dict[Coord, PlayerColor]) -> list[Coord]:
    """
    Construct a vertical line for a coord.
    """
    line = []
    for i in range(BOARD_N):
        if not board.get(Coord(i, coord.c), None):
            line.append(Coord(i, coord.c))
    return line
        
def reconstruct_path(came_from: dict[Coord, Coord | None], current: Coord | None) -> list[Coord | None]:
    """
    Reconstruct the path from the start to the current node.
    """
    total_path = [current]
    while current in came_from:
        current = came_from[current]
        total_path.append(current)
    return total_path[::-1]

def reconstruct_pieces(parent_move: dict[PlaceAction, PlaceAction], goal_piece: PlaceAction) -> list[PlaceAction]:
    path = []
    current_piece = goal_piece
    while current_piece is not NONE_PIECE:
        path.append(current_piece)
        current_piece = parent_move[current_piece]
    path.reverse()  # Reverse the path to go from start to goal
    return path

def perform_move(board: dict[Coord, PlayerColor], move: PlaceAction) -> dict[Coord, PlayerColor]:
    """
    Perform a list of PlaceActions on the board.
    """
    for coord in move.coords:
        board[coord] = PlayerColor.RED
    return board


# check all 19 possible moves, check if valid, if valid, add to list of possible moves
# for each possible move, calculate the cost of the move
# edge cost calculated from furthest coord of current to closest coord of next
# need to create some data structure to represent a piece (4 coords)

# add each coord to piece seperately, using add method (overridden in Coord class)

# find path to goal, then fill in? then back track, filling in first?
