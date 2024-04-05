from .core import PlayerColor, Coord, PlaceAction, Direction

BOARD_N = 11

# TODO: make more efficient heuristic/s
def calculate_heuristic(board, goal_line):
    """
    Calculate the heuristic cost for the given board.
    The heuristic is the number of empty spaces in the goal line + the distance to the goal line + the number of pieces above the goal line + the number of holes.
    """
    empty_spaces = sum(1 for coord in goal_line if board.get(coord, None) is None)
    return pow(empty_spaces * 10, 2) + calculate_distance_to_goal_line(board, goal_line) 
# + calculate_pieces_above_goal_line(board, goal_line) + calculate_number_of_holes(board)

def calculate_distance_to_goal_line(board, goal_line: list[Coord]):
    total_distance = 0
    num_pieces = 0
    for coord, color in board.items():
        if color is PlayerColor.RED:  # if there is a piece at this coordinate
            distance = min(distance_between_coords(goal_coord, coord) for goal_coord in goal_line)
            total_distance += distance
            num_pieces += 1
    return total_distance / num_pieces if num_pieces else 0

def calculate_pieces_above_goal_line(board, goal_line:list[Coord]):
    """
    Prioritise states where there are fewer pieces above the goal line, as these pieces could potentially block the goal line from being filled.
    """
    highest_goal_coord = max(coord.r for coord in goal_line)
    return sum(1 for coord, color in board.items() if color is not None and coord.r > highest_goal_coord)


def calculate_number_of_holes(board):
    """
    Prioritise states with fewer holes, as holes can make it more difficult to fill the goal line.
    """
    holes = 0
    for x in range(BOARD_N):
        column = [board.get(Coord(x, y), None) for y in range(BOARD_N)]
        if None in column:
            first_empty = column.index(None)
            holes += sum(1 for cell in column[first_empty:] if cell is not None)
    return holes

def distance_between_coords(coord1, coord2):
    row = min(abs(coord1.r - coord2.r), BOARD_N - abs(coord1.r - coord2.r))
    col = min(abs(coord1.c - coord2.c), BOARD_N - abs(coord1.c - coord2.c))
    return row + col