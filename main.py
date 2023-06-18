from typing import NamedTuple

from ClausesManager import ClausesManager
from hitman.hitman import HC, HitmanReferee
from movement import move_forward, turn_anti_clockwise, is_valid_position, is_blocked, turn_clockwise, \
    positions_are_adjacent, get_actions_moves, get_adjacent_positions, get_successor_score, get_orientation_case
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

    start_exploring(room, status)

    # Start phase 2
    # function_phase_2()


def start_exploring(room, status):
    # TODO change move
    #explore(room, set(), status)
    explore_dfs(room, status)
    ClausesManager.write_dimacs_files(ClausesManager.clauses)
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
        #input("Press Enter to continue...")

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
            #input("Press Enter to continue...")
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
                            if is_valid_position(move_forward(position, orientation), room):
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
            if is_valid_position(successor, room) and successor not in visited:
                successors_score.append((successor, get_successor_score(successor, room, ClausesManager, get_orientation_case(position, successor))))
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
                        (successor, get_successor_score(successor, room, ClausesManager, get_orientation_case(position, successor))))
        if is_discovered(room):
            break
        successor_max = successors_score[0]
        st.append(successor_max[0])

        # logs
        print("Visited: ", visited)
        print("Stack: ", st)
        print("Movements: ", movements)
        print("successors_score", successors_score)
        #input()
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
