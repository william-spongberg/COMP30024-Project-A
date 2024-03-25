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
    #print("goal:", goal)

    # a_star_search
    #path = a_star_search(board, start, goal)
    #print(path)
    
    # change goal as needed? e.g. change to the closest row/col line
    # decide which row/col line is best -> most filled, closest to start
    
    # path find from coord to coord of line, saving path up to last piece in pieces variable
    # different goal-checking method now - not adjacent to goal, but on the line (coords)
    
    
    h_line = contruct_horizontal_line(goal, board)
    v_line = construct_vertical_line(goal, board)
    # temp get smaller line, change to heuristic later
    line = h_line if len(h_line) < len(v_line) else v_line
    
    print("goals:", line)
    
    path = a_star_search(board, start, line, goal)
    
    """
    while line:
        _, line_coord = find_closest_coords(start, line)
        line.remove(line_coord)
        path = a_star_search(board, start, line_coord)
        if path:
            start = path[-1]
        else:
            break
    """
        
    # need to remove line_coords from line as they are covered in a_star
            
    # heuristic to fill line or manually fill line?
      
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

def a_star_search(board: dict[Coord, PlayerColor], start_piece: PlaceAction, goal_line: list[Coord], goal: Coord) -> list[PlaceAction] | None:
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
    
    start_coord, current_goal = find_closest_coords(start_piece, goal_line)    
    heapq.heappush(open_set, (0, start_coord))  # heap is initialized with start node
    came_from_coord = {start_coord: None}
    came_from_piece = {start_coord: start_piece}
    g = {start_coord: 0}
    f = {start_coord: heuristic_to_line(start_piece, start_coord, current_goal, came_from_coord, goal_line)}

    while open_set:
        _, current_coord = heapq.heappop(open_set)  # node with lowest f_score is selected
        expanded_nodes += 1

        for coord in came_from_piece[current_coord].coords:
            if coord == None:
                continue
            
            if coord in goal_line:
                print("removed", coord)
                goal_line.remove(coord)
                
            # if no more goals
            if not goal_line:
                path += reconstruct_path(came_from_coord, current_coord)
                #pieces = list(dict.fromkeys(path))
                pieces += reconstruct_pieces(path, came_from_piece)
                # print solution
                for piece in pieces:
                    perform_move(board, piece)
                print("\nSOLUTION:")
                print(render_board(board, goal, ansi=True))
                # remove duplicates
                pieces = list(dict.fromkeys(pieces))
                return pieces[1:]
            
            # can only be on goal if not actual final goal, found line goal
            if coord == current_goal:
                # reset starting from current piece
                current_goal = find_closest_line_coord(coord, goal_line)
                # check if None (even though cannot logically occur)
                if current_goal == None:
                    print("ERROR: current_goal is None")
                    current_goal = goal
                
                # TODO: fix blocking coords to be completed
                # TODO: fix pieces not being placed properly
                # TODO: fix duplicate pieces, not going back to initial piece properly - fix with starting coord? no came_from_coord should work right
                # put moves in board
                path += reconstruct_path(came_from_coord, current_coord)
                #pieces = list(dict.fromkeys(path))
                pieces += reconstruct_pieces(path, came_from_piece)
                for piece in pieces:
                    perform_move(board, piece)
                continue
            
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
            
            # find next moves
            for adjacent_coord in get_valid_adjacents(board, coord):
                for move in get_valid_moves(board, tetronimos, adjacent_coord, reconstruct_pieces(reconstruct_path(came_from_coord, current_coord), came_from_piece)):
                    move_coord = find_closest_coord(move, current_goal)

                    if move not in came_from_piece and move_coord not in came_from_coord:
                        generated_nodes += 1
                        came_from_coord[move_coord] = current_coord
                        came_from_piece[move_coord] = move
                        g[move_coord] = g[current_coord] + heuristic_to_line(came_from_piece[current_coord], current_coord, move_coord, came_from_coord, goal_line)
                        f[move_coord] = g[move_coord] + heuristic_to_line(move, move_coord, current_goal, came_from_coord, goal_line)
                        heapq.heappush(open_set, (f[move_coord], move_coord))
                        
                        # print last two pieces
                        board_temp = board.copy()
                        if (came_from_piece[move_coord] != None):
                            perform_move(board_temp, came_from_piece[current_coord])
                        print(render_board(perform_move(board_temp, move), current_goal, ansi=True))
                        print("coord:", move_coord, "h:", heuristic_to_line(came_from_piece[current_coord], current_coord, move_coord, came_from_coord, goal_line), "+", heuristic_to_line(move, move_coord, goal, came_from_coord, goal_line))
                        print("current goal:", current_goal)
                        print("goal line:", goal_line)
                        print("generated nodes:", generated_nodes)
                        print("expanded nodes:", expanded_nodes)
                        print("duplicate nodes:", duplicated_nodes)
                    else:
                        duplicated_nodes += 1
                        
    return None  # path not found

def get_valid_moves(board: dict[Coord, PlayerColor], tetronimos: list[PlaceAction], coord: Coord, prev_moves: list[PlaceAction]) -> list[PlaceAction]:
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
    #print("valid:", valid_adjacents)
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
    return min(abs(a.r - b.r), BOARD_N - abs(a.r - b.r)) + min(abs(a.c - b.c), BOARD_N - abs(a.c - b.c))

def heuristic_piece(piece: PlaceAction, coord: Coord, goal: Coord, came_from_coord: dict[Coord, Coord | None]) -> int:
    """
    Calculate a heuristic for a piece based on the Manhattan distance to the goal and the number of pieces in the path so far.
    """
    manhattan_distance = sum([heuristic(coord, goal) for coord in piece.coords if coord != None])
    return manhattan_distance + count_pieces(came_from_coord, coord)

def heuristic_to_line(piece: PlaceAction, coord: Coord, goal: Coord, came_from_coord: dict[Coord, Coord | None], line: list[Coord]) -> int:
    """
    Calculate a heuristic for a piece based on the maximum Manhattan distance to the goal and the number of pieces in the path and goal line.
    """
    manhattan_distance = sum([heuristic(coord, goal) for coord in piece.coords if coord != None])
    for line_coord in line:
        if sum([heuristic(coord, line_coord) for coord in piece.coords if coord != None]) > manhattan_distance:
            manhattan_distance = sum([heuristic(coord, line_coord) for coord in piece.coords if coord != None])
    return manhattan_distance + count_pieces(came_from_coord, coord) + len(line)

def count_pieces(came_from_coord: dict[Coord, Coord | None], coord: Coord | None) -> int:
    """
    Count the number of pieces in the path to the current node.
    """
    pieces = 0
    while (coord in came_from_coord):
        coord = came_from_coord[coord]
        pieces += 1
    return pieces

def contruct_horizontal_line(coord: Coord, board: dict[Coord, PlayerColor]) -> list[Coord]:
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

def reconstruct_pieces(coords: list[Coord | None], came_from_piece: dict[Coord | None, PlaceAction]) -> list[PlaceAction]:
    """
    Reconstruct pieces used for path
    """
    pieces = []
    for coord in coords:
        if coord != None:
            piece = came_from_piece[coord]
            pieces.append(piece)
    return pieces

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
