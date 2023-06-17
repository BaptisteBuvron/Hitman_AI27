from typing import List

from hitman.hitman import HC


def move_forward(position, orientation, step = 1):
    # Move one cell forward in the current orientation
    i, j = position
    if orientation == HC.N:
        return (i, j + step)
    elif orientation == HC.S:
        return (i, j - step)
    elif orientation == HC.W:
        return (i - step, j)
    elif orientation == HC.E:
        return (i + step, j)


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


def opposite_orientation_guard(orientation):
    # Turn to the next orientation (anticlockwise)
    if orientation == HC.N:
        return HC.GUARD_S
    elif orientation == HC.W:
        return HC.GUARD_E
    elif orientation == HC.S:
        return HC.GUARD_N
    elif orientation == HC.E:
        return HC.GUARD_W
    pass

    # Turn to the next orientation (anticlockwise)
    if orientation == HC.N:
        return HC.S
    elif orientation == HC.W:
        return HC.E
    elif orientation == HC.S:
        return HC.N
    elif orientation == HC.E:
        return HC.W

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

def positions_are_adjacent(position1, position2):
    # Check if the two positions are adjacent
    i1, j1 = position1
    i2, j2 = position2
    if abs(i1 - i2) + abs(j1 - j2) == 1:
        return True
    return False

def get_actions_adjacents(current, adjacent_position, actions):
    # Get the actions to go from the current position to the adjacent positions
    while current != adjacent_position:
        if current[1] == adjacent_position[1]:
            if current[1] < adjacent_position[1]:
                actions.append(HC.MOVE_FORWARD)
                current = (current[0], current[1] + 1)
            else:
                actions.append(HC.TURN_CLOCKWISE)
                current = turn_clockwise(current)

    return actions

def get_adjacent_positions(position, room, n_row, n_col, orientation = HC.N):
    st=[]
    orientation_temp = orientation
    for i in range(4):
        neightboard = is_valid_position(move_forward(position, orientation_temp), room, n_row, n_col)
        if neightboard:
            st.append(move_forward(position, orientation_temp))
        orientation_temp = turn_clockwise(orientation_temp)
    return st

def get_actions_moves(position, goal, orientation):
    actions = []
    dy = goal[1] - position[1]
    dx = goal[0] - position[0]

    if dy > 0:
        if orientation == HC.N:
            actions.append("move")
        elif orientation == HC.E:
            actions.append("turn_anti_clockwise")
            actions.append("move")
        elif orientation == HC.S:
            actions.append("turn_clockwise")
            actions.append("turn_clockwise")
            actions.append("move")
        elif orientation == HC.W:
            actions.append("turn_clockwise")
            actions.append("move")

    elif dy < 0:
        if orientation == HC.N:
            actions.append("turn_clockwise")
            actions.append("turn_clockwise")
            actions.append("move")
        elif orientation == HC.E:
            actions.append("turn_clockwise")
            actions.append("move")
        elif orientation == HC.S:
            actions.append("move")
        elif orientation == HC.W:
            actions.append("turn_anti_clockwise")
            actions.append("move")

    if dx > 0:
        if orientation == HC.N:
            actions.append("turn_clockwise")
            actions.append("move")
        elif orientation == HC.E:
            actions.append("move")
        elif orientation == HC.S:
            actions.append("turn_anti_clockwise")
            actions.append("move")
        elif orientation == HC.W:
            actions.append("turn_clockwise")
            actions.append("turn_clockwise")
            actions.append("move")
    elif dx < 0:
        if orientation == HC.N:
            actions.append("turn_anti_clockwise")
            actions.append("move")
        elif orientation == HC.E:
            actions.append("turn_clockwise")
            actions.append("turn_clockwise")
            actions.append("move")
        elif orientation == HC.S:
            actions.append("turn_clockwise")
            actions.append("move")
        elif orientation == HC.W:
            actions.append("move")

    return actions

def guard_orientation_to_orientation(orientation):
    if orientation == HC.GUARD_N:
        return HC.N
    elif orientation == HC.GUARD_E:
        return HC.E
    elif orientation == HC.GUARD_S:
        return HC.S
    elif orientation == HC.GUARD_W:
        return HC.W