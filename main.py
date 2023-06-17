import os
from pprint import pprint
from hitman.hitman import HC, HitmanReferee, complete_map_example
from utils import OS
import subprocess

# globals
N_ROW = 7
N_COL = 7
N_GUEST = None
N_GUARD = None
VARIABLES = dict()
CLAUSES = list()
OS_USER: OS = OS.none
DEBUG: bool = True
BLOCKED_CELLS = set(tuple())
HR: HitmanReferee


def main():
    global VARIABLES
    global HR
    HR = HitmanReferee()

    room, status = start_phase1()
    create_clauses()

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
    global HR, N_ROW, N_COL, N_GUARD, N_GUEST
    status = HR.start_phase1()
    N_ROW = int(status["m"])
    N_COL = int(status["n"])
    N_GUARD = int(status["guard_count"])
    N_GUEST = int(status["civil_count"])
    create_variables()
    room = [[0 for j in range(N_COL)] for i in range(N_ROW)]
    analyse_status(status, room)
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
        # Il y a un garde dans une des 4 cases autour de nous
        pass
    if status["hear"]:
        # On a entendu x garde ou un civil
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
    # CHOOSE an ORIENTATION (turn_clockwise, turn_anti_clockwise) or GO FORWARD
    if is_discovered(room):
        return
    if is_blocked(room, visited, position, orientation):
        print("BLOCKED")
        if is_valid_position(move_forward(position, orientation), room):
            print("Blocked, GO FORWARD")
            explore(room, visited, HR.move())
        else:
            print("Blocked, TURN ANTICLOCKWISE")
            explore(room, visited, HR.turn_anti_clockwise())

    #Choose the next move to optimize the new explored cells (is_position_discovered())
    #For each move, we check the number of new cells supposed discovered
    #We choose the move with the most new cells discovered

    dict_choose_move = dict()
    for move in ["move", "turn_anti_clockwise", "turn_clockwise", "double_turn"]:
        if move == "move":
            if is_valid_position(move_forward(position, orientation), room):
                dict_choose_move[move] = count_max_new_cells_discovered(room, move_forward(position,orientation), orientation)
            else:
                dict_choose_move[move] = -1
        elif move == "turn_anti_clockwise":
            dict_choose_move[move] = count_max_new_cells_discovered(room, position, turn_anti_clockwise(orientation))
        elif move == "turn_clockwise":
            dict_choose_move[move] = count_max_new_cells_discovered(room, position, turn_clockwise(orientation))
        elif move == "double_turn":
            dict_choose_move[move] = count_max_new_cells_discovered(room, position, turn_clockwise(turn_clockwise(orientation)))

    print(dict_choose_move)
    #We choose the move with the most new cells discovered
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
        analyse_status(status, room)
        status = HR.turn_clockwise()
        analyse_status(status, room)
        explore(room, visited, status)



    # if is_valid_position(move_forward(position, turn_anti_clockwise(orientation)), room) and move_forward(position,
    #                                                                                                       turn_anti_clockwise(
    #                                                                                                           orientation)) not in visited:
    #     print("TURN ANTI CLOCKWISE")
    #     explore(room, visited, HR.turn_anti_clockwise())
    # elif is_valid_position(move_forward(position, orientation), room) and move_forward(position,
    #                                                                                    orientation) not in visited:
    #     print("GO FORWARD")
    #     explore(room, visited, HR.move())
    # else:
    #     print("TURN CLOCKWISE")
    #     explore(room, visited, HR.turn_clockwise())


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
    #Hitman can see 3 cells in front of him
    for i in range(3):
        if is_valid_position(move_forward(position, orientation), room):
            position = move_forward(position, orientation)
            if not is_position_discovered(position, room):
                count += 1
        else:
            return count
    return count

def is_blocked(room, visited, position, orientation):
    """
    Check if the hitman is blocked (all the cells around him are walls, guards or visited)
    :param room:
    :param visited:
    :param position:
    :param orientation:
    :return: True if the hitman is blocked
    """
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
    """
    Check if the position is within the room boundaries and not a wall or a guard
    :param position:
    :param room:
    :return: True if the position is valid
    """
    # Check if the position is within the room boundaries and not a wall
    i, j = position
    if (
            0 <= i < N_COL
            and 0 <= j < N_ROW
            and room[N_ROW - 1 - j][i]
            not in [HC.WALL, HC.GUARD_E, HC.GUARD_N, HC.GUARD_S, HC.GUARD_W]
    ):
        return True
    return False


def move_forward(position, orientation):
    """
    Move one cell forward in the current orientation
    :param position:
    :param orientation:
    :return: the new position
    """
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
    """
    Turn to the next orientation (clockwise)
    :param orientation:
    :return the new orientation
    """
    if orientation == HC.N:
        return HC.E
    elif orientation == HC.E:
        return HC.S
    elif orientation == HC.S:
        return HC.W
    elif orientation == HC.W:
        return HC.N


def turn_anti_clockwise(orientation):
    """
    Turn to the next orientation (anti-clockwise)
    :param orientation:
    :return the new orientation
    """
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


def add_clauses_map_test():
    global CLAUSES
    for key in complete_map_example:
        CLAUSES.append([get_variable(HC.EMPTY, key[0], key[1])])


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


def check_current_directory():
    if os.getcwd() != os.path.dirname(os.path.realpath(__file__)):
        print("Please execute this script from the root directory")
        exit(1)


if __name__ == "__main__":
    main()
