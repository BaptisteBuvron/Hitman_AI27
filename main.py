from typing import NamedTuple

from ClausesManager import ClausesManager
from hitman.hitman import HC, HitmanReferee
from movement import (
    move_forward,
    turn_anti_clockwise,
    is_valid_position,
    is_blocked,
    turn_clockwise,
    positions_are_adjacent,
    get_actions_moves,
    get_adjacent_positions,
    get_successor_score,
    get_orientation_case,
    get_best_move,
)
from phase_2 import function_phase_2

# globals

HR: HitmanReferee
ClausesManager: ClausesManager
N_ROW = 10
N_COL = 10
debug = False


def main():
    global ClausesManager, N_ROW, N_COL, debug
    global HR
    HR = HitmanReferee()
    status = HR.start_phase1()
    N_ROW = status["m"]
    N_COL = status["n"]
    room = [[0 for j in range(status["n"])] for i in range(status["m"])]
    position = status["position"]
    room[N_ROW - 1 - int(position[1])][int(position[0])] = HC.EMPTY
    ClausesManager = ClausesManager(
        status["m"], status["n"], status["guard_count"], status["civil_count"], debug
    )
    ClausesManager.analyse_status(status, room)

    correct_map = start_exploring(room, status)
    input("\nAppuyez sur entrée pour continuer avec la phase 2...")

    # Start phase 2
    function_phase_2(HR, correct_map)


def start_exploring(room, status):
    # TODO change move
    # explore(room, set(), status)
    # explore_dfs(room, status)
    explore_v3(room, status)
    # transform room to map_info: Dict[Tuple[int, int], List[HC]]
    map_info = {}
    for i in range(len(room[0])):
        for j in range(len(room)):
            map_info[(i, j)] = room[N_ROW - 1 - j][i]
    # End phase 1
    print(HR.send_content(map_info))
    success, score, history, correct_map = HR.end_phase1()
    print("Success: ", success)
    print("Correct map: ", correct_map)
    print("Score de la phase 1: ", score)

    # ClausesManager.write_dimacs_files(ClausesManager.clauses)
    return correct_map


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
        if is_valid_position(move_forward(position, orientation), room):
            print("Blocked, GO FORWARD")
            explore(room, visited, HR.move())
        else:
            print("Blocked, TURN CLOCKWISE")
            explore(room, visited, HR.turn_clockwise())

    if (
        is_valid_position(
            move_forward(position, turn_anti_clockwise(orientation)), room
        )
        and move_forward(position, turn_anti_clockwise(orientation)) not in visited
    ):
        print("TURN ANTI CLOCKWISE")
        explore(room, visited, HR.turn_anti_clockwise())
    elif (
        is_valid_position(move_forward(position, orientation), room)
        and move_forward(position, orientation) not in visited
    ):
        print("GO FORWARD")
        explore(room, visited, HR.move())
    else:
        print("TURN CLOCKWISE")
        explore(room, visited, HR.turn_clockwise())


def explore_v3(room, status):
    global ClausesManager
    position = status["position"]
    orientation = HC(status["orientation"])
    error = False
    deducted = 0

    while not is_discovered(room) and not error:
        move = get_best_move(room, position, orientation, ClausesManager)
        actions = get_actions_moves(position, move, orientation)
        action = actions[0]
        print("actions", actions)
        if action == "turn_anti_clockwise":
            status = HR.turn_anti_clockwise()
            ClausesManager.analyse_status(status, room)
        elif action == "turn_clockwise":
            status = HR.turn_clockwise()
            ClausesManager.analyse_status(status, room)
        elif action == "move":
            status = HR.move()
            ClausesManager.analyse_status(status, room)
        if status["status"] != "OK":
            print("ERROR")
            error = True
        position = status["position"]
        orientation = HC(status["orientation"])
        print("move: ", move)
        print("action: ", action)
        if not ClausesManager.debug:
            # deduct only 4 cases arround the hitman
            positions = ClausesManager.get_positions_around(position, 2)
            deducted += ClausesManager.deduct(room, positions)
        # input("press enter to continue")
        pass

    pass
    print("Finished")
    print("Deducted case: ", deducted)


def explore_dfs_v1(room, status):
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
                        if is_valid_position(move_forward(position, orientation), room):
                            movements.append(position)
                            status = HR.move()
                            ClausesManager.analyse_status(status, room)
                            neighbors = get_adjacent_positions(cur, room)
                        else:
                            print("Blocked...")
                    position = status["position"]
                    print("cur: ", cur)
                    print("position", position)
                    print("st", st)
            else:
                while cur != position and not is_discovered(room):
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
                            if is_valid_position(
                                move_forward(position, orientation), room
                            ):
                                if is_adjacent:
                                    neighbors = get_adjacent_positions(cur, room)
                                    movements.append(position)
                                status = HR.move()
                                ClausesManager.analyse_status(status, room)
                            else:
                                visited.add(cur)
                                cur = st.pop()
                        position = status["position"]
        else:
            neighbors = get_adjacent_positions(cur, room)
        for neighbor in neighbors:
            if neighbor not in visited:
                st.append(neighbor)

        # logs
        print("Visited: ", visited)
        print("Stack: ", st)
        print("Movements: ", movements)
        # input("Press Enter to continue...")


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
        if status["is_in_guard_range"]:
            print("GUARDED", ClausesManager.guarded_positions)
            print("cur: ", cur)
            # input("Press Enter to continue...")
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
                        if is_valid_position(move_forward(position, orientation), room):
                            movements.append(position)
                            status = HR.move()
                            ClausesManager.analyse_status(status, room)
                            neighbors = get_adjacent_positions(cur, room)
                        else:
                            print("Blocked...")
                    position = status["position"]
                    print("cur: ", cur)
                    print("position", position)
                    print("st", st)
            else:
                while cur != position and not is_discovered(room):
                    is_adjacent = False
                    # On est retourné en arrière jusqu'a que le but soit une case adjacente
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
                            if is_valid_position(
                                move_forward(position, orientation), room
                            ):
                                if is_adjacent:
                                    neighbors = get_adjacent_positions(cur, room)
                                    movements.append(position)
                                status = HR.move()
                                ClausesManager.analyse_status(status, room)
                            else:
                                visited.add(cur)
                                cur = st.pop()
                        position = status["position"]
        else:
            neighbors = get_adjacent_positions(cur, room)
        successors_score = []
        print("neighbors", neighbors)
        print("guarded", ClausesManager.guarded_positions)
        for successor in neighbors:
            # TODO not visited
            if is_valid_position(successor, room) and successor not in visited:
                successors_score.append(
                    (
                        successor,
                        get_successor_score(
                            successor,
                            room,
                            ClausesManager,
                            get_orientation_case(position, successor),
                        ),
                    )
                )
        print("successors_score", successors_score)
        # get max successor

        successors_score.sort(key=lambda x: x[1], reverse=True)
        print("successors_score", successors_score)
        # On retourne en arrière jusqu'a trouver un noeud avec des successeurs non visités

        while len(successors_score) < 1 and not is_discovered(room):
            print("NO SUCCESSORS: GO BACK")
            actions = get_actions_moves(position, movements.pop(), orientation)
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
                    if is_valid_position(move_forward(position, orientation), room):
                        status = HR.move()
                        ClausesManager.analyse_status(status, room)
                    else:
                        visited.add(cur)
                position = status["position"]
            neighbors = get_adjacent_positions(position, room)
            for successor in neighbors:
                if is_valid_position(successor, room) and successor not in visited:
                    successors_score.append(
                        (
                            successor,
                            get_successor_score(
                                successor,
                                room,
                                ClausesManager,
                                get_orientation_case(position, successor),
                            ),
                        )
                    )
        if is_discovered(room):
            break
        successor_max = successors_score[0]
        st.append(successor_max[0])

        # logs
        print("Visited: ", visited)
        print("Stack: ", st)
        print("Movements: ", movements)
        print("successors_score", successors_score)
        # input()


# input("Press Enter to continue...")


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
