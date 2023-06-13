from ClausesManager import ClausesManager
from hitman.hitman import HC, HitmanReferee
from movement import move_forward, turn_anti_clockwise, is_valid_position, is_blocked

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
    ClausesManager = ClausesManager(status["m"], status["n"], status["guard_count"], status["civil_count"])
    ClausesManager.analyse_status(status, room)

    start_exploring(room, status)


    # Start phase 2
    function_phase_2()

def start_exploring(room, status):
    visited = set()
    # TODO change move
    explore(room, visited, status)
    return room


def explore(room, visited, status):
    global ClausesManager
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


if __name__ == "__main__":
    main()
