# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part A: Single Player Tetress

from .core import PlayerColor, Coord, PlaceAction, Direction
from .utils import render_board
from typing import Optional
from math import inf
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
    
    # search on both lines
    # the variables below are used to limit further searches if a solution is found
    has_solution = False
    lowest_g = inf
    
    path_h = a_star_search(board, start, h_line, goal, has_solution, lowest_g)
    path_v = a_star_search(board, start, v_line, goal, has_solution, lowest_g)
    
    print("lowest_g:", lowest_g)
    
    if (path_h == None):
        print("No solution for h.")
        path = path_v
    elif (path_v == None):
        print("No solution for v.")
        path = path_h
    else:
        print("Both solutions found. Picking shortest")
        print("h:", len(path_h), "v:", len(path_v))
        path =  path_h if len(path_h) < len(path_v) else path_v
        
    print("path:", path)
    return path
    
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

def a_star_search(board: dict[Coord, PlayerColor], start_piece: PlaceAction, goal_line: list[Coord], 
                  goal: Coord, has_solution: bool, lowest_g: float) -> list[PlaceAction] | None:
    """
    Perform an A* search to find the shortest path from start to goal.
    """
    tetronimos = get_tetronimos()
    open_set = []
    
    generated_nodes = 0
    expanded_nodes = 0
    # find that the current logic to avoid duplicate nodes is wrong and it removes correct nodes,
    # so comment out for now
    # duplicated_nodes = 0

    heapq.heappush(open_set, (0, 0, board))  # heap is initialized with start node
    frozen_board = frozenset(board.items())
    parent_move = {frozen_board: start_piece} # parent of each board, using NONE_PIECE to avoid type errors
    g = {frozen_board: 0} # g represents the steps
    # heuristic is now judging the whole board, not just the new move
    f = {frozen_board: heuristic_to_goal(board, goal_line)}

    solution = None
    
    while open_set:
        _, _, current_board = heapq.heappop(open_set)  # node with lowest f_score is selected
        expanded_nodes += 1
        current_board_frozen = frozenset(current_board.items())
        # already found a solution with lower g, skip
        if has_solution and g[current_board_frozen]+1 >= lowest_g:
            continue
        # find next moves
        for adjacent_coord in get_valid_adjacents_all_over_the_board(current_board, goal_line):
            for move in get_valid_moves(current_board, tetronimos, adjacent_coord):
                generated_nodes += 1
                new_board = get_current_board(current_board, move)
                new_board_frozen = frozenset(new_board.items())
                if new_board_frozen in g and g[new_board_frozen] <= g[current_board_frozen] + 1:
                    continue
                parent_move[new_board_frozen] = move
                
                # perform move on board
                g[new_board_frozen] = g[current_board_frozen] + 1
                f[new_board_frozen] = g[new_board_frozen] + heuristic_to_goal(new_board, goal_line)
                # if goal line is filled, print success message
                if all([new_board.get(coord, None) for coord in goal_line]):
                    print(render_board(new_board, goal, ansi=True))
                    print("Success! Path found.")
                    print("length:", g[new_board_frozen])
                    # update best solution state
                    if not has_solution:
                        has_solution = True
                        lowest_g = g[new_board_frozen]
                        solution = reconstruct_pieces(parent_move, new_board)
                        return solution
                    else:
                        if g[new_board_frozen] < lowest_g:
                            lowest_g = g[new_board_frozen]
                            solution = reconstruct_pieces(parent_move, new_board)
                heapq.heappush(open_set, (f[new_board_frozen], generated_nodes, new_board))
                # print debug info
                print(render_board(new_board, goal, ansi=True))
                print("move:", move, "g:", g[new_board_frozen], "f:", f[new_board_frozen])
                print("goal:", goal)
                print("goal line:", goal_line)
                print("generated nodes:", generated_nodes)
                print("expanded nodes:", expanded_nodes)
                # print("duplicate nodes:", duplicated_nodes)
                # else:
                #     duplicated_nodes += 1          
    return solution

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
    # valid_adjacents.sort(key=lambda x: heuristic_to_line(x, goal_line))
    return valid_adjacents

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

def get_current_board(base_board: dict[Coord, PlayerColor], piece: PlaceAction) -> dict[Coord, PlayerColor]:
    """
    Get the current board state after placing a piece.
    """
    temp_board = base_board.copy()
    for coord in piece.coords:
        temp_board[coord] = PlayerColor.RED
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

def reconstruct_pieces(parent_move: dict[frozenset[tuple[Coord, PlayerColor]], PlaceAction], board: dict[Coord, PlayerColor]) -> list[PlaceAction]:
    path = []
    current_board = frozenset(board.items())
    while current_board in parent_move:
        move = parent_move[current_board]
        path.append(move)
        prev_board = set(current_board)
        for coord in move.coords:
            if coord is None:
                continue
            prev_board.remove((coord, PlayerColor.RED))
        current_board = frozenset(prev_board)
    path.reverse()
    return path


# check all 19 possible moves, check if valid, if valid, add to list of possible moves
# for each possible move, calculate the cost of the move
# edge cost calculated from furthest coord of current to closest coord of next
# need to create some data structure to represent a piece (4 coords)

# add each coord to piece seperately, using add method (overridden in Coord class)

# find path to goal, then fill in? then back track, filling in first?
