import heapq

from hitman.hitman import HC


def move_forward(position, orientation, step=1):
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
    # TODO refactor n_row, n_col
    # If all square arround are walls,guard or visited
    turn = turn_clockwise(orientation)
    if (
            is_valid_position(move_forward(position, orientation), room)
            and move_forward(position, orientation) not in visited
    ):
        return False
    if (
            is_valid_position(move_forward(position, turn), room)
            and move_forward(position, turn) not in visited
    ):
        return False
    if (
            is_valid_position(
                move_forward(position, turn_anti_clockwise(orientation)), room)
            and move_forward(position, turn_anti_clockwise(orientation)) not in visited
    ):
        return False
    if (
            is_valid_position(move_forward(position, turn_clockwise(turn)), room)
            and move_forward(position, turn_clockwise(turn)) not in visited
    ):
        return False
    return True


def is_valid_position(position, room):
    # Check if the position is within the room boundaries and not a wall
    n_row, n_col = len(room), len(room[0])
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


def get_adjacent_positions(position, room, orientation=HC.S):
    st = []
    orientation_temp = orientation
    for i in range(4):
        neightboard = is_valid_position(move_forward(position, orientation_temp), room)
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


def get_successor_score(successor, room, ClausesManager, orientation):
    n_row = len(room)
    if room[n_row - 1 - int(successor[1])][int(successor[0])] in [HC.CIVIL_N, HC.CIVIL_S, HC.CIVIL_E,
                                                                  HC.CIVIL_W]:
        return 2 + (count_max_new_cells_discovered(room, successor, orientation)*5)
    elif (successor in ClausesManager.guarded_positions) and room[n_row - 1 - int(successor[1])][
        int(successor[0])] not in [HC.WALL, HC.GUARD_N, HC.GUARD_S, HC.GUARD_E,
                                   HC.GUARD_W]:
        return -5
    if room[n_row - 1 - int(successor[1])][int(successor[0])] in [HC.EMPTY, HC.TARGET, HC.SUIT, HC.PIANO_WIRE]:
        return 1 + (count_max_new_cells_discovered(room, successor, orientation)*5)

    elif room[n_row - 1 - int(successor[1])][int(successor[0])] not in [HC.WALL, HC.GUARD_N, HC.GUARD_S, HC.GUARD_E,
                                                                        HC.GUARD_W]:
        return 5 + (count_max_new_cells_discovered(room, successor, orientation)*5)


def count_max_new_cells_discovered(room, position, orientation):
    """
    Count the number of new cells discovered from a position and an orientation
    :param room:
    :param position:
    :param orientation:
    :return: the number of new cells discovered
    """
    count = 0
    # Hitman can see 3 cells in front of him
    for i in range(1,4):
        if is_valid_position(move_forward(position, orientation, i), room) and get_type_of_room(room, move_forward(position, orientation, i)) not in (HC.CIVIL_S, HC.CIVIL_N, HC.CIVIL_E, HC.CIVIL_W):
            position_new = move_forward(position, orientation,i)
            if not is_position_discovered(position_new, room):
                count += 1
        else:
            return count
    return count

def get_type_of_room(room, position):
    N_ROW = len(room)
    return room[N_ROW - 1 - int(position[1])][int(position[0])]

def is_position_discovered(position, room):
    """
    Check if the position is already discovered
    :param room:
    :param position:
    :return: True if the position is already discovered
    """
    return room[len(room) - 1 - position[1]][position[0]] != 0


def get_orientation_case(position, case):
    dy = case[1] - position[1]
    dx = case[0] - position[0]
    if dy > 0:
        return HC.N
    elif dy < 0:
        return HC.S
    elif dx > 0:
        return HC.E
    elif dx < 0:
        return HC.W


def get_best_move(room, position, orientation, ClausesManager):
    successors = get_adjacent_positions(position, room, orientation)
    successors_scores = []
    for successor in successors:
        successors_scores.append((successor, get_successor_score(successor, room, ClausesManager, get_orientation_case(position, successor))))
    successors_scores.sort(key=lambda x: x[1], reverse=True)
    if successors_scores[0][1] < 5:
        print("Dijkstra")
        return get_next_unexplored_position(room, position, ClausesManager)
    return successors_scores[0][0]


def get_next_unexplored_position(room, position, ClauseManager):
    #use dijkstra to get the next unexplored position
    unexplored_position = []
    for i in range(len(room)):
        for j in range(len(room[0])):
            if get_type_of_room(room, (j, i)) not in [HC.GUARD_E, HC.GUARD_N, HC.GUARD_S, HC.GUARD_W, HC.CIVIL_E, HC.CIVIL_N, HC.CIVIL_S, HC.CIVIL_W,
                 HC.TARGET, HC.SUIT, HC.PIANO_WIRE, HC.EMPTY, HC.WALL]:
                unexplored_position.append(((j, i), dijkstra(room, position, (j, i), ClauseManager)))
    unexplored_position.sort(key=lambda x: x[1][1])
    print(unexplored_position)
    return unexplored_position[0][1][0][1]

def get_neighbors(room, position):
    """
    Get the neighboring positions of a given position in the room
    :param room: the room map
    :param position: the position to get the neighbors of
    :return: a list of neighboring positions
    """
    neighbors = []
    x, y = position

    # Check the four adjacent positions
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        new_x = x + dx
        new_y = y + dy

        # Check if the new position is within the room boundaries
        if 0 <= new_x < len(room[0]) and 0 <= new_y < len(room):
            neighbors.append((new_x, new_y))

    return neighbors
def dijkstra(room, position,goal, ClausesManager):
    """
    Dijkstra algorithm to find the shortest path between two points
    :param room:
    :param position:
    :param goal:
    :return: the shortest path between position and goal
    """
    room_priority = [[0] * len(room[0]) for _ in range(len(room))]
    for j in range(len(room)):
        for i in range(len(room[0])):
            if (i,j) in ClausesManager.guarded_positions and get_type_of_room(room, (i,j)) not in [HC.WALL, HC.GUARD_N, HC.GUARD_S, HC.GUARD_E, HC.GUARD_W]:
                room_priority[j][i] = 5
            elif get_type_of_room(room, (i,j)) in [HC.EMPTY, HC.TARGET, HC.SUIT, HC.PIANO_WIRE, HC.CIVIL_E, HC.CIVIL_N, HC.CIVIL_S, HC.CIVIL_W]:
                room_priority[j][i] = 1
            else:
                room_priority[j][i] = 1000000000
    room_priority[goal[1]][goal[0]] = 0

    # Initialize the distance matrix with infinite values
    distances = [[float('inf')] * len(room[0]) for _ in range(len(room))]
    distances[position[1]][position[0]] = 0

    # Create a priority queue to store the vertices and their distances
    pq = [(0, position)]

    # Create a dictionary to store the previous vertex for each vertex in the shortest path
    previous = {}

    while pq:
        current_distance, current_vertex = heapq.heappop(pq)

        # Stop if we reach the goal
        if current_vertex == goal:
            break

        # Skip this vertex if we have already found a shorter path to it
        if current_distance > distances[current_vertex[1]][current_vertex[0]]:
            continue

        # Explore all neighboring vertices
        for neighbor in get_neighbors(room, current_vertex):
            neighbor_distance = current_distance + room_priority[neighbor[1]][neighbor[0]]

            # Update the distance and previous vertex if a shorter path is found
            if neighbor_distance < distances[neighbor[1]][neighbor[0]]:
                distances[neighbor[1]][neighbor[0]] = neighbor_distance
                previous[neighbor] = current_vertex
                heapq.heappush(pq, (neighbor_distance, neighbor))

    # Reconstruct the shortest path
    path = []
    current_vertex = goal
    while current_vertex != position:
        path.append(current_vertex)
        current_vertex = previous[current_vertex]
    path.append(position)
    path.reverse()
    return path, distances[goal[1]][goal[0]]


    pass