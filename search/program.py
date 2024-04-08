# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part A: Single Player Tetress

from .core import PlayerColor, Coord, PlaceAction
from .utils import render_board
from .tetronimos import get_tetronimos
from .heuristics import calculate_heuristic
from .movements import get_valid_moves, get_valid_adjacents_all_over_the_board
from .lines import delete_filled_lines

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
    
    path = a_search(board, start, goal)
    
    return path

def a_search(board: dict[Coord, PlayerColor], start_piece: PlaceAction, 
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

    g = {frozenset(board.items()): len(start_piece.coords)}  # cost from start to current node
    f = {frozenset(board.items()): calculate_heuristic(board, goal, start_piece, [start_piece])}  # f = g + h

    generated_nodes = 0
    duplicated_nodes = 0

    while queue:
        _, current_board_id = heapq.heappop(queue)  # node with lowest f_score is selected
        current_board = board_dict[current_board_id]
        current_board_frozen = frozenset(current_board.items())
        # find next moves
        for adjacent_coord in get_valid_adjacents_all_over_the_board(current_board, goal):
            for move in get_valid_moves(current_board, tetronimos, adjacent_coord):
                new_board = get_current_board(current_board, move)
                new_board = delete_filled_lines(new_board)
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
                g[new_board_frozen] = g[current_board_frozen] + 4  # update the cost from start to current node
                
                # if goal coord has been removed from board
                if goal not in new_board:
                    print(render_board(new_board, goal, ansi=True))
                    print(f"Generated nodes: {generated_nodes}")
                    print(f"Duplicated nodes: {duplicated_nodes}")
                    
                    path = reconstruct_path(predecessors, new_board)
                    
                    # for debug
                    result_board = board.copy()
                    print(render_board(result_board, goal, ansi=True))
                    for action in path[1:-1]:
                        result_board = get_current_board(result_board, action)
                        delete_filled_lines(result_board)
                        print(render_board(result_board, goal, ansi=True))
                    result_board = get_current_board(result_board, path[-1])
                    print(render_board(result_board, goal, ansi=True))
                    print(f"Generated nodes: {generated_nodes}")
                    print(f"Duplicated nodes: {duplicated_nodes}")
                    
                    # test tetronimos
                    # empty_board = {}
                    # for action in tetronimos:
                    #     center_coord = Coord(5, 5)
                    #     action = PlaceAction(*[center_coord + coord for coord in action.coords])
                    #     print(render_board(get_current_board(empty_board, action), goal, ansi=True))
                        
                    return path[1:]  # remove the start move
                
                # path = reconstruct_path(predecessors, new_board)
                heuristic_cost = calculate_heuristic(new_board, goal, move, reconstruct_path(predecessors, new_board))
                #if g[new_board_frozen] > heuristic_cost:
                   # g[new_board_frozen] = heuristic_cost + 8
                    
                f[new_board_frozen] = g[new_board_frozen] + heuristic_cost
                heapq.heappush(queue, (f[new_board_frozen], board_id))
                
                print(render_board(new_board, goal, ansi=True))
                print(f"Generated nodes: {generated_nodes}")
                print(f"Duplicated nodes: {duplicated_nodes}")
                print(f"Current g: {g[new_board_frozen]}")
                print(f"Current h: {heuristic_cost}")
    return None

def reconstruct_path(predecessors: dict, end: dict) -> list[PlaceAction]:
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

def get_current_board(base_board: dict[Coord, PlayerColor], piece: PlaceAction) -> dict[Coord, PlayerColor]:
    """
    Get the current board state after placing a piece.
    """
    temp_board = base_board.copy()
    for coord in piece.coords:
        temp_board[coord] = PlayerColor.RED
    return temp_board