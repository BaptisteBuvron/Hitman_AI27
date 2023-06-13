from hitman.hitman import HC


def move_forward(position, orientation):
    # Move one cell forward in the current orientation
    i, j = position
    if orientation == HC.N:
        return (i, j + 1)
    elif orientation == HC.S:
        return (i, j - 1)
    elif orientation == HC.W:
        return (i - 1, j)
    elif orientation == HC.E:
        return (i + 1, j)


def turn_clockwise(orientation):
    # Turn to the next orientation (clockwise)
    if orientation == HC.N:
        return HC.E
    elif orientation == HC.E:
        return HC.S
    elif orientation == HC.S:
        return HC.W
    elif orientation == HC.W:
        return HC.N


def turn_anti_clockwise(orientation):
    # Turn to the next orientation (anticlockwise)
    if orientation == HC.N:
        return HC.W
    elif orientation == HC.W:
        return HC.S
    elif orientation == HC.S:
        return HC.E
    elif orientation == HC.E:
        return HC.N


def is_blocked(room, visited, position, orientation, n_row, n_col):
    #TODO refactor n_row, n_col
    # If all square arround are walls,guard or visited
    turn = turn_clockwise(orientation)
    if (
        is_valid_position(move_forward(position, orientation), room, n_row, n_col)
        and move_forward(position, orientation) not in visited
    ):
        return False
    if (
        is_valid_position(move_forward(position, turn), room, n_row, n_col)
        and move_forward(position, turn) not in visited
    ):
        return False
    if (
        is_valid_position(
            move_forward(position, turn_anti_clockwise(orientation)), room, n_row, n_col
        )
        and move_forward(position, turn_anti_clockwise(orientation)) not in visited
    ):
        return False
    if (
        is_valid_position(move_forward(position, turn_clockwise(turn)), room, n_row, n_col)
        and move_forward(position, turn_clockwise(turn)) not in visited
    ):
        return False
    return True


def is_valid_position(position, room, n_row, n_col):
    # Check if the position is within the room boundaries and not a wall
    i, j = position
    if is_inside_room(position, n_row, n_col) and room[n_row - 1 - j][i] not in [
        HC.WALL,
        HC.GUARD_E,
        HC.GUARD_N,
        HC.GUARD_S,
        HC.GUARD_W,
    ]:
        return True
    return False


def is_inside_room(position, n_row, n_col):
    # Check if the position is within the room boundaries
    i, j = position
    if 0 <= i < n_col and 0 <= j < n_row:
        return True
    return False

