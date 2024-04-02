from .core import PlayerColor, Coord, PlaceAction, Direction

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

def count_pieces(came_from: dict[Coord, Coord | None], coord: Coord | None) -> int:
    """
    Count the number of pieces in the path to the current node.
    """
    pieces = 0
    while (coord in came_from):
        coord = came_from[coord]
        pieces += 1
    return pieces