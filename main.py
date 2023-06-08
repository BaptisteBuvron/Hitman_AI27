import itertools
import json
import os
import subprocess
from pprint import pprint
from typing import List

from sympy import to_cnf, symbols, Or

from hitman.hitman import HC, HitmanReferee, complete_map_example
from utils import OS

# globals
N_ROW = 7
N_COL = 7
N_CIVIL = 5
N_GUARD = 5
VARIABLES = dict()
CLAUSES = list()
OS_USER: OS = OS.none
DEBUG: bool = True
BLOCKED_CELLS = set(tuple())
SEEN_CELLS = set(tuple())
HR: HitmanReferee


def main():
    global VARIABLES
    global HR
    HR = HitmanReferee()

    room, status = start_phase1()
    create_clauses()
    analyse_status(status, room)

    start_exploring(room, status)

    # if (DEBUG):
    #     add_clauses_map_test()
    write_dimacs_files()
    execute_gophersat()


def start_exploring(room, status):
    visited = set()
    # TODO change move
    explore(room, visited, status)
    return room


def start_phase1():
    global HR, N_ROW, N_COL, N_GUARD, N_CIVIL
    status = HR.start_phase1()
    N_ROW = int(status["m"])
    N_COL = int(status["n"])
    N_GUARD = int(status["guard_count"])
    N_CIVIL = int(status["civil_count"])
    create_variables()
    room = [[0 for j in range(N_COL)] for i in range(N_ROW)]
    return room, status


def analyse_status(status, room):
    global CLAUSES, BLOCKED_CELLS
    pprint(status)
    # From the vision of the hitman, we can see the type of the 2 cells in front of him
    for vision in status["vision"]:
        # TODO Add unsafe cells (gards, walls)
        if room[N_ROW - 1 - int(vision[0][1])][int(vision[0][0])] == 0:
            # (0,0) is the bottom left corner
            room[N_ROW - 1 - int(vision[0][1])][int(vision[0][0])] = HC(vision[1])
            CLAUSES.append(
                [get_variable(HC(vision[1]), int(vision[0][0]), int(vision[0][1]))]
            )
            if HC(vision[1]) == HC.WALL:
                BLOCKED_CELLS.add((int(vision[0][0]), int(vision[0][1])))

    if status["is_in_guard_range"]:
        clauses = []
        top = move_forward(status["position"], HC.N)
        if is_inside_room(top):
            clauses.append(get_variable(HC.GUARD_S, top[0], top[1]))
        left = move_forward(status["position"], HC.W)
        if is_inside_room(left):
            clauses.append(get_variable(HC.GUARD_E, left[0], left[1]))
        right = move_forward(status["position"], HC.E)
        if is_inside_room(right):
            clauses.append(get_variable(HC.GUARD_W, right[0], right[1]))
        bottom = move_forward(status["position"], HC.S)
        if is_inside_room(bottom):
            clauses.append(get_variable(HC.GUARD_N, bottom[0], bottom[1]))
        CLAUSES.append(clauses)
        pass
    else:
        # Il n'y a pas de garde dans les 4 cases autour de nous
        top = move_forward(status["position"], HC.N)
        if is_valid_position(top, room):
            CLAUSES.append([-get_variable(HC.GUARD_S, top[0], top[1])])
        left = move_forward(status["position"], HC.W)
        if is_valid_position(left, room):
            CLAUSES.append([-get_variable(HC.GUARD_E, left[0], left[1])])
        right = move_forward(status["position"], HC.E)
        if is_valid_position(right, room):
            CLAUSES.append([-get_variable(HC.GUARD_W, right[0], right[1])])
        bottom = move_forward(status["position"], HC.S)
        if is_valid_position(bottom, room):
            CLAUSES.append([-get_variable(HC.GUARD_N, bottom[0], bottom[1])])
    if status["hear"] != 0:
        # Il y a x gardes ou un invités dans une des 4 cases autour de nous
        pass
    else:
        # Vérifier combien de garde ou de civils qui ne sont pas dans la zone d'écoute, si la soustraction est en dessous de 5 ajouter les clauses.
        pass
    if DEBUG:
        # beautifull print of the array [][] room
        for i in range(N_ROW):
            for j in range(N_COL):
                longueur = 15
                print(room[i][j], end=" " * (longueur - len(str(room[i][j]))))
            print()
    pass


def explore(room, visited, status):
    position = status["position"]
    analyse_status(status, room)
    orientation = HC(status["orientation"])
    visited.add(position)
    print("Visited: ", visited)
    # input 0 to exit the function
    write_dimacs_files()
    choice = input("Enter 0 to exit the function: ")
    if choice == "0":
        print("EXIT")
        return

    # CHOOSE an ORIENTATION (turn_clockwise, turn_anti_clockwise) or GO FORWARD

    if is_blocked(room, visited, position, orientation):
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


def is_blocked(room, visited, position, orientation):
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
            move_forward(position, turn_anti_clockwise(orientation)), room
        )
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
    i, j = position
    if is_inside_room(position) and room[N_ROW - 1 - j][i] not in [
        HC.WALL,
        HC.GUARD_E,
        HC.GUARD_N,
        HC.GUARD_S,
        HC.GUARD_W,
    ]:
        return True
    return False


def is_inside_room(position):
    # Check if the position is within the room boundaries
    i, j = position
    if 0 <= i < N_COL and 0 <= j < N_ROW:
        return True
    return False


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


def get_os():
    global OS_USER
    if OS_USER == OS.none:
        print("What OS are you using?")
        valid_os = [os for os in OS if os != OS.none]
        for os in valid_os:
            print(str(os.value) + ": " + os.name)
        os = int(input())
        # set OS from the input
        if os not in [os.value for os in valid_os]:
            print("Invalid OS")
            get_os()
        OS_USER = OS(os)
    return OS_USER


def create_variables():
    global VARIABLES
    dict = {}
    variable: int = 1
    for i in range(0, N_COL):
        for j in range(0, N_ROW):
            for type in HC:
                if type not in [HC.N, HC.S, HC.E, HC.W]:
                    # I = row, J = COL
                    dict["_".join([str(type.value), str(i), str(j)])] = variable
                    variable += 1
    VARIABLES = dict


def get_variable(type, row: int, col: int):
    return VARIABLES["_".join([str(type.value), str(row), str(col)])]


def create_clauses():
    global CLAUSES
    # Clauses 1: Each cell has a type (EMPTY or WALL or GUARD_N...)
    clause = []
    for i in range(0, N_COL):
        for j in range(0, N_ROW):
            for type in HC:
                if type not in [HC.N, HC.S, HC.E, HC.W]:
                    clause.append(get_variable(type, i, j))
            CLAUSES.append(clause)
            clause = []

    # Clauses 2: Each cell has only one type
    for i in range(0, N_COL):
        for j in range(0, N_ROW):
            for type in HC:
                if type not in [HC.N, HC.S, HC.E, HC.W]:
                    for type2 in HC:
                        if type2 not in [HC.N, HC.S, HC.E, HC.W] and type != type2:
                            CLAUSES.append(
                                [-get_variable(type, i, j), -get_variable(type2, i, j)]
                            )

    # Clauses 3: The cell PIANO_WIRE / Target / Suit exists only one time
    clausePiano = []
    clauseSuit = []
    clauseTarget = []
    for i in range(0, N_COL):
        for j in range(0, N_ROW):
            clausePiano.append(-get_variable(HC.PIANO_WIRE, i, j))
            clauseSuit.append(-get_variable(HC.SUIT, i, j))
            clauseTarget.append(-get_variable(HC.TARGET, i, j))
    CLAUSES.append(clausePiano)
    CLAUSES.append(clauseSuit)
    CLAUSES.append(clauseTarget)

    # If the cell is a PIANO_WIRE/TARGET/SUIT, all the other cells are not a PIANO_WIRE/TARGET/SUIT
    for i in range(0, N_COL):
        for j in range(0, N_ROW):
            for k in range(i, N_COL):
                for l in range(j, N_ROW):
                    if i != k or j != l:
                        for type in [HC.PIANO_WIRE, HC.SUIT, HC.TARGET]:
                            CLAUSES.append(
                                [-get_variable(type, i, j), -get_variable(type, k, l)]
                            )

    write_dimacs_files()


def create_clauses_max_type(types: List, max: int):
    # Il y a exactement 2 guards test array 3*3
    positions = []
    for i in range(0, N_COL):
        for j in range(0, N_ROW):
            positions.append((i, j))

    # get all values of dict
    values = list(VARIABLES.values())
    ls = symbols(" ".join([str(i) for i in values]))
    combinations = list(itertools.combinations(positions, max))
    print(combinations)
    number = 0
    for comb in combinations:
        print(
            "Treatment of combination " + str(number) + " / " + str(len(combinations))
        )
        number += 1
        other = []
        for i in positions:
            if i not in comb:
                other.append(i)
        dnf = []
        for i in comb:
            clause = []
            for type in types:
                clause.append(-get_variable(type, i[0], i[1]))
            dnf.append(clause)
        clause = []
        for j in other:
            for type in types:
                clause.append(-get_variable(type, j[0], j[1]))
        dnf.append(clause)
        dnf_string = ""
        for clause in dnf:
            if dnf_string != "":
                dnf_string += " | "
            dnf_string += "("
            for i in clause:
                if dnf_string[-1] != "(":
                    dnf_string += " & "
                if i < 0:
                    dnf_string += "~ls[" + str(abs(i) - 1) + "]"
                else:
                    dnf_string += "ls[" + str(i - 1) + "]"
            dnf_string += ")"
        cnf = to_cnf(eval(dnf_string), simplify=False, force=True)
        cnf = list(cnf.args)
        for c in cnf:
            clause = []
            for i in c.args:
                clause.append(int(str(i).replace("~", "-")))
            CLAUSES.append(clause)


def add_clauses_map_test():
    global CLAUSES
    for key in complete_map_example:
        CLAUSES.append([get_variable(HC.EMPTY, key[0], key[1])])


def check_current_directory():
    if os.getcwd() != os.path.dirname(os.path.realpath(__file__)):
        print("Please execute this script from the root directory")
        exit(1)


def write_dimacs_files():
    global CLAUSES
    check_current_directory()
    # Write the clauses in a file if exists replace it
    with open("gophersat/hitman.cnf", "w") as f:
        f.write("p cnf " + str(len(VARIABLES)) + " " + str(len(CLAUSES)) + "\n")
        for clause in CLAUSES:
            f.write(" ".join([str(x) for x in clause]) + " 0\n")
    pass


def execute_gophersat():
    check_current_directory()
    os_user = get_os()
    gophersat_path = ""
    if os_user == OS.WINDOWS:
        gophersat_path = "gophersat/gophersat.exe"
    elif os_user == OS.LINUX:
        gophersat_path = "gophersat/gophersat"
    elif os_user == OS.MAC_amd:
        gophersat_path = "gophersat/gophersat_1_13_darwin_amd64"
    elif os_user == OS.MAC_arm:
        gophersat_path = "gophersat/gophersat_1_13_darwin_arm64"
    result = subprocess.run(
        [gophersat_path, "gophersat/hitman.cnf"], capture_output=True, text=True
    )
    print(result.stdout)


def export_clauses_to_file():
    check_current_directory()
    nameFile = (
        "clauses/clauses_"
        + str(N_COL)
        + "_"
        + str(N_ROW)
        + "_"
        + str(N_GUARD)
        + "_"
        + str(N_CIVIL)
        + ".json"
    )
    with open(nameFile, "w") as f:
        json.dump(CLAUSES, f)


def import_clauses_from_file():
    global CLAUSES
    check_current_directory()
    nameFile = (
        "clauses/clauses_"
        + str(N_COL)
        + "_"
        + str(N_ROW)
        + "_"
        + str(N_GUARD)
        + "_"
        + str(N_CIVIL)
        + ".json"
    )
    # if file exists
    if os.path.isfile(nameFile):
        with open(nameFile, "r") as f:
            CLAUSES = json.load(f)
            return True
    return False


if __name__ == "__main__":
    main()
