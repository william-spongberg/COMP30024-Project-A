from .core import PlayerColor, Coord, PlaceAction, Direction
from .tetronimos import get_moves
from .heuristics import coord_distance_to_goal_line

def get_valid_moves(board: dict[Coord, PlayerColor], tetronimos: list[PlaceAction], coord: Coord) -> list[PlaceAction]:
    """
    Get valid PlaceActions from a given coordinate.
    """
    valid_moves = []
    
    # for each piece, check if valid, if valid, add to list of possible moves
    for move in get_moves(coord, tetronimos):
        if is_valid(board, move):
            valid_moves.append(move)
    return valid_moves

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
    valid_adjacents.sort(key=lambda x: coord_distance_to_goal_line(goal_line, x))
    return valid_adjacents

def is_valid(board: dict[Coord, PlayerColor], piece: PlaceAction) -> bool:
    """
    Check if the piece can be placed on the board.
    """
    for coord in piece.coords:
        if board.get(coord, None):
            return False
    return True