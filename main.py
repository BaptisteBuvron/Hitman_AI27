from ClausesManager import ClausesManager
from hitman.hitman import HC, HitmanReferee
from movement import move_forward, turn_anti_clockwise, is_valid_position, is_blocked, turn_clockwise, \
    positions_are_adjacent, get_actions_moves, get_adjacent_positions
from phase_2 import function_phase_2

# globals

HR: HitmanReferee
ClausesManager: ClausesManager
N_ROW = 10
N_COL = 10


def main():
    global ClausesManager, N_ROW, N_COL
    global HR
    HR = HitmanReferee()
    status = HR.start_phase1()
    N_ROW = status["m"]
    N_COL = status["n"]
    room = [[0 for j in range(status["n"])] for i in range(status["m"])]
    position = status["position"]
    room[N_ROW - 1 - int(position[1])][int(position[0])] = HC.EMPTY
    ClausesManager = ClausesManager(status["m"], status["n"], status["guard_count"], status["civil_count"])
    ClausesManager.analyse_status(status, room)

    position1 = (0, 0)
    position2 = (0, 1)
    print(positions_are_adjacent(position1, position2))
    print(get_actions_moves(position1, position2, HC.S))

    start_exploring(room, status)

    # Start phase 2
    # function_phase_2()


def start_exploring(room, status):
    visited = set()
    # TODO change move
    explore_dfs(room, status)
    return room


def explore(room, visited, status):
    global ClausesManager
    if is_discovered(room):
        print("DISCOVERED")
        return
    position = status["position"]
    ClausesManager.analyse_status(status, room)
    orientation = HC(status["orientation"])
    visited.add(position)
    print("Visited: ", visited)
    # input 0 to exit the function

    # CHOOSE an ORIENTATION (turn_clockwise, turn_anti_clockwise) or GO FORWARD

    if is_blocked(room, visited, position, orientation, N_ROW, N_COL):
        print("BLOCKED")
        if is_valid_position(move_forward(position, orientation), room, N_ROW, N_COL):
            print("Blocked, GO FORWARD")
            explore(room, visited, HR.move())
        else:
            print("Blocked, TURN CLOCKWISE")
            explore(room, visited, HR.turn_clockwise())

    if (
            is_valid_position(
                move_forward(position, turn_anti_clockwise(orientation)), room, N_ROW, N_COL
            )
            and move_forward(position, turn_anti_clockwise(orientation)) not in visited
    ):
        print("TURN ANTI CLOCKWISE")
        explore(room, visited, HR.turn_anti_clockwise())
    elif (
            is_valid_position(move_forward(position, orientation), room, N_ROW, N_COL)
            and move_forward(position, orientation) not in visited
    ):
        print("GO FORWARD")
        explore(room, visited, HR.move())
    else:
        print("TURN CLOCKWISE")
        explore(room, visited, HR.turn_clockwise())


def explore_dfs(room, status):
    global ClausesManager
    if is_discovered(room):
        print("DISCOVERED")
        return
    position = status["position"]
    orientation = HC(status["orientation"])
    st = [position]
    movements = []
    visited = set()
    print("dfs")



    while len(st) > 0 and not is_discovered(room):
        cur = st.pop()
        visited.add(cur)
        # ADD predecessor


        if position != cur:
            if positions_are_adjacent(position, cur):
                actions = get_actions_moves(position, cur, orientation)
                for action in actions:
                    print(action)
                    if action == "turn_anti_clockwise":
                        status = HR.turn_anti_clockwise()
                        ClausesManager.analyse_status(status, room)
                        orientation = HC(status["orientation"])
                    elif action == "turn_clockwise":
                        print("turn_clockwise")
                        status = HR.turn_clockwise()
                        ClausesManager.analyse_status(status, room)
                        orientation = HC(status["orientation"])
                    elif action == "move":
                        if is_valid_position(move_forward(position, orientation), room, N_ROW, N_COL):
                            movements.append(position)
                            status = HR.move()
                            ClausesManager.analyse_status(status, room)
                            neighbors = get_adjacent_positions(cur, room, N_ROW, N_COL)
                        else:
                            print("Blocked...")
                    position = status["position"]
                    print("cur: ", cur)
                    print("position", position)
                    print("st", st)
            else:
                while cur != position:
                    is_adjacent = False
                    if positions_are_adjacent(position, cur):
                        actions = get_actions_moves(position, cur, orientation)
                        is_adjacent = True
                    else:
                        movement = movements.pop()
                        print("movement", movement)
                        actions = get_actions_moves(position, movement, orientation)
                    print("GO BACK")
                    print("cur: ", cur)
                    print("position", position)
                    print("movements", movements)
                    for action in actions:
                        print(action)
                        if action == "turn_anti_clockwise":
                            status = HR.turn_anti_clockwise()
                            ClausesManager.analyse_status(status, room)
                            orientation = HC(status["orientation"])
                        elif action == "turn_clockwise":
                            status = HR.turn_clockwise()
                            ClausesManager.analyse_status(status, room)
                            orientation = HC(status["orientation"])
                        elif action == "move":
                            if is_valid_position(move_forward(position, orientation), room, N_ROW, N_COL):
                                if is_adjacent:
                                    neighbors = get_adjacent_positions(cur, room, N_ROW, N_COL)
                                    movements.append(position)
                                status = HR.move()
                                ClausesManager.analyse_status(status, room)
                            else:
                                visited.add(cur)
                                cur = st.pop()
                        position = status["position"]
        else:
            neighbors = get_adjacent_positions(cur, room, N_ROW, N_COL)
        for neighbor in neighbors:
            if neighbor not in visited:
                st.append(neighbor)

        # logs
        print("Visited: ", visited)
        print("Stack: ", st)
        print("Movements: ", movements)


def explore_(room, visited, status):
    global ClausesManager
    if is_discovered(room):
        print("DISCOVERED")
        return
    position = status["position"]
    ClausesManager.analyse_status(status, room)
    orientation = HC(status["orientation"])
    visited.add(position)
    print("Visited: ", visited)
    # CHOOSE an ORIENTATION (turn_clockwise, turn_anti_clockwise) or GO FORWARD
    if is_blocked(room, visited, position, orientation, N_ROW, N_COL):
        print("BLOCKED")
        if is_valid_position(move_forward(position, orientation), room, N_ROW, N_COL):
            print("Blocked, GO FORWARD")
            explore(room, visited, HR.move())
        else:
            print("Blocked, TURN ANTICLOCKWISE")
            explore(room, visited, HR.turn_anti_clockwise())

    # Choose the next move to optimize the new explored cells (is_position_discovered())
    # For each move, we check the number of new cells supposed discovered
    # We choose the move with the most new cells discovered

    dict_choose_move = dict()
    for move in ["move", "turn_anti_clockwise", "turn_clockwise", "double_turn"]:
        if move == "move":
            if is_valid_position(move_forward(position, orientation), room, N_ROW, N_COL):
                dict_choose_move[move] = count_max_new_cells_discovered(room, move_forward(position, orientation),
                                                                        orientation)
            else:
                dict_choose_move[move] = -1
        elif move == "turn_anti_clockwise":
            dict_choose_move[move] = count_max_new_cells_discovered(room, position, turn_anti_clockwise(orientation))
        elif move == "turn_clockwise":
            dict_choose_move[move] = count_max_new_cells_discovered(room, position, turn_clockwise(orientation))
        elif move == "double_turn":
            dict_choose_move[move] = count_max_new_cells_discovered(room, position,
                                                                    turn_clockwise(turn_clockwise(orientation)))

    print(dict_choose_move)
    # We choose the move with the most new cells discovered
    move = max(dict_choose_move, key=dict_choose_move.get)
    if move == "move":
        print("MOVE")
        explore(room, visited, HR.move())
    elif move == "turn_clockwise":
        print("TURN CLOCKWISE")
        explore(room, visited, HR.turn_clockwise())
    elif move == "turn_anti_clockwise":
        print("TURN ANTI CLOCKWISE")
        explore(room, visited, HR.turn_anti_clockwise())
    elif move == "double_turn":
        print("DOUBLE TURN")
        status = HR.turn_clockwise()
        ClausesManager.analyse_status(status, room)
        status = HR.turn_clockwise()
        ClausesManager.analyse_status(status, room)
        explore(room, visited, status)


def is_position_discovered(position, room):
    """
    Check if the position is already discovered
    :param room:
    :param position:
    :return: True if the position is already discovered
    """
    return room[N_ROW - 1 - position[1]][position[0]] != 0


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
    for i in range(3):
        if is_valid_position(move_forward(position, orientation), room, N_ROW, N_COL):
            position = move_forward(position, orientation)
            if not is_position_discovered(position, room):
                count += 1
        else:
            return count
    return count


def is_discovered(room) -> bool:
    """
    Check if all the cells are discovered
    :param room:
    :return: True if all the cells are discovered
    """
    for row in room:
        for cell in row:
            if cell == 0:
                return False
    return True


if __name__ == "__main__":
    main()
