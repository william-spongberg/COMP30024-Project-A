# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part A: Single Player Tetress

from .core import PlayerColor, Coord, PlaceAction, Direction
from .utils import render_board
from .tetronimos import get_tetronimos
from .heuristics import calculate_heuristic
from .movements import get_valid_moves, get_valid_adjacents_all_over_the_board
from .lines import construct_horizontal_line, construct_vertical_line

from typing import Tuple
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
    
    h_line = construct_horizontal_line(goal, board)
    v_line = construct_vertical_line(goal, board)

    line = h_line if len(h_line) < len(v_line) else v_line
    path = a_search(board, start, line, goal)
        
    #print("path:", path)
    return path

# TODO: can optimise by recording valid adjacent moves in a dict
# TODO: alter heuristic to want to cover as many goal coords in one move as possible

def a_search(board: dict[Coord, PlayerColor], start_piece: PlaceAction, goal_line: list[Coord], 
                  goal: Coord) -> list[PlaceAction] | None:
    """
    Perform an A* search to find the shortest path from start to goal.
    """
    tetronimos = get_tetronimos()
    queue = []  # queue is initialized with start node
    board_id = 0  # unique identifier for each board
    heapq.heappush(queue, (0, board_id))  # priority, board_id
    board_dict = {board_id: board}  # map each board_id to its corresponding board
    move_dict = {frozenset(board.items()): start_piece}  # map each board to its corresponding move
    visited = set([frozenset(board.items())])  # visited set is initialized with start node
    predecessors: dict[frozenset, Tuple[frozenset, PlaceAction]] = {frozenset(board.items()): (frozenset(), start_piece)}  # dictionary to keep track of predecessors

    generated_nodes = 0
    duplicated_nodes = 0

    while queue:
        _, current_board_id = heapq.heappop(queue)  # node with lowest f_score is selected
        current_board = board_dict[current_board_id]
        current_board_frozen = frozenset(current_board.items())
        # find next moves
        for adjacent_coord in get_valid_adjacents_all_over_the_board(current_board, goal_line):
            for move in get_valid_moves(current_board, tetronimos, adjacent_coord):
                new_board = get_current_board(current_board, move)
                new_board_frozen = frozenset(new_board.items())
                generated_nodes += 1
                if new_board_frozen in visited:
                    duplicated_nodes += 1
                    continue
                
                visited.add(new_board_frozen)
                board_id += 1
                board_dict[board_id] = new_board  # update the board for the new board_id
                move_dict[new_board_frozen] = move  # update the move for the new board
                predecessors[new_board_frozen] = (current_board_frozen, move)  # update the predecessor of the new node
                
                # if goal line is filled, return the path
                if all([new_board.get(coord, None) for coord in goal_line]):
                    print(render_board(new_board, goal, ansi=True))
                    print(f"Generated nodes: {generated_nodes}")
                    print(f"Duplicated nodes: {duplicated_nodes}")
                    
                    path = reconstruct_path(predecessors, new_board)
                    new_board = delete_goal_line(new_board, goal_line)
                    print(render_board(new_board, goal, ansi=True))
                    return path[1:]  # remove the start move
                #new_board = delete_filled_lines(new_board)
                
                # calculate heuristic cost
                heuristic_cost = calculate_heuristic(new_board, goal)
                heapq.heappush(queue, (heuristic_cost, board_id))
    print(f"Generated nodes: {generated_nodes}")
    print(f"Duplicated nodes: {duplicated_nodes}")
    return None

def reconstruct_path(predecessors: dict, end: dict) -> list:
    """
    Reconstruct the path from start to end using the predecessors dictionary.
    """
    path = []
    current = frozenset(end.items())
    while current is not None:
        current, action = predecessors.get(current, (None, None))
        if action is not None:
            path.append(action)
    path.reverse()  # reverse the path to get it from start to end
    return path

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

def delete_goal_line(board: dict[Coord, PlayerColor], goal_line: list[Coord]) -> dict[Coord, PlayerColor]:
    """
    Delete the coordinates on the goal line from the board.
    """
    if goal_line[0].r == goal_line[1].r:  # check if goal line is horizontal
        goal_line_rows = {coord.r for coord in goal_line}
        for coord in list(board.keys()):  # create a copy of keys to iterate over
            if coord.r in goal_line_rows:
                del board[coord]
    else:  # goal line is vertical
        goal_line_cols = {coord.c for coord in goal_line}
        for coord in list(board.keys()):  # create a copy of keys to iterate over
            if coord.c in goal_line_cols:
                del board[coord]
    return board

def delete_filled_lines(board: dict[Coord, PlayerColor]):
    # Get all unique row and column indices
    rows = {coord.r for coord in board.keys()}
    cols = {coord.c for coord in board.keys()}

    # Check each row
    for r in rows:
        row_coords = [coord for coord in board.keys() if coord.r == r]
        if all(board[coord] is not None for coord in row_coords):
            # If all coordinates in the row are filled, delete them
            for coord in row_coords.copy():  # create a copy of row_coords to iterate over
                del board[coord]

    # Check each column
    for c in cols:
        col_coords = [coord for coord in board.keys() if coord.c == c]
        if all(board[coord] is not None for coord in col_coords):
            # If all coordinates in the column are filled, delete them
            for coord in col_coords.copy():  # create a copy of col_coords to iterate over
                del board[coord]

    return board