# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part A: Single Player Tetress

from .core import PlayerColor, Coord, PlaceAction, Direction
from .utils import render_board
from .tetronimos import get_tetronimos, get_moves
from .heuristics import heuristic_to_goal, heuristic_to_line
from .movements import get_valid_moves, get_valid_adjacents_all_over_the_board, is_valid
from .lines import construct_horizontal_line, construct_vertical_line
from .pieces import reconstruct_pieces, count_pieces

from typing import Optional
from math import inf
import heapq
from collections import deque

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
    
    h_line = construct_horizontal_line(goal, board)
    v_line = construct_vertical_line(goal, board)
    
    # search on both lines
    # the variables below are used to limit further searches if a solution is found
    has_solution = False
    lowest_g = inf
    
    """
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
        path = path_h if len(path_h) < len(path_v) else path_v
    """
    line = h_line if len(h_line) < len(v_line) else v_line
    path = bfs_search(board, start, line, goal)
        
    print("path:", path)
    return path

# TODO: can optimise by recording valid adjacent moves in a dict
# TODO: alter heuristic to want to cover as many goal coords in one move as possible

def bfs_search(board: dict[Coord, PlayerColor], start_piece: PlaceAction, goal_line: list[Coord], 
               goal: Coord) -> list[PlaceAction] | None:
    """
    Perform a BFS search to find the shortest path from start to goal.
    """
    tetronimos = get_tetronimos()
    queue = deque([(start_piece, board)])  # queue is initialized with start node
    visited = set([frozenset(board.items())])  # visited set is initialized with start node
    predecessors = {frozenset(board.items()): frozenset()}  # dictionary to keep track of predecessors

    while queue:
        current_piece, current_board = queue.popleft()  # node with lowest f_score is selected
        current_board_frozen = frozenset(current_board.items())
        # find next moves
        for adjacent_coord in get_valid_adjacents_all_over_the_board(current_board, goal_line):
            for move in get_valid_moves(current_board, tetronimos, adjacent_coord):
                new_board = get_current_board(current_board, move)
                new_board_frozen = frozenset(new_board.items())
                if new_board_frozen in visited:
                    continue
                visited.add(new_board_frozen)
                predecessors[new_board_frozen] = current_board_frozen  # update the predecessor of the new node
                # if goal line is filled, return the path
                if all([new_board.get(coord, None) for coord in goal_line]):
                    print(render_board(new_board, goal, ansi=True))
                    return reconstruct_path(predecessors, new_board)
                queue.append((move, new_board))
    return None

def reconstruct_path(predecessors: dict, end: dict) -> list:
    """
    Reconstruct the path from start to end using the predecessors dictionary.
    """
    path = []
    current = frozenset(end.items())
    while current is not None:
        path.append(dict(current))
        current = predecessors.get(current)
    path.reverse()  # reverse the path to get it from start to end
    return path

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
        check_row_and_col(temp_board, coord)
    return temp_board

def check_row_and_col(board: dict[Coord, PlayerColor], coord: Coord):
    """
    Check if a row and column is filled, if so remove them.
    """
    row = [board.get(Coord(coord.r, i), None) for i in range(BOARD_N)]
    col = [board.get(Coord(i, coord.c), None) for i in range(BOARD_N)]
    if all(row):
        for i in range(BOARD_N):
            del board[Coord(coord.r, i)]
    if all(col):
        for i in range(BOARD_N):
            del board[Coord(i, coord.c)]
    return