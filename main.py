import os
from hitman.hitman import HC, complete_map_example
from utils import OS
import subprocess


#globals
N_ROW = 7
N_COL = 7
VARIABLES = dict()
CLAUSES = list()
OS_USER: OS = OS.none
DEBUG: bool = False

def main():
    global VARIABLES 
    VARIABLES = create_variables()
    create_clauses()
    if (DEBUG):
        add_clauses_map_test()
    write_dimacs_files()
    execute_gophersat()


def get_os():
    global OS_USER
    if OS_USER == OS.none:
        print("What OS are you using?")
        valid_os = [os for os in OS if os != OS.none]
        for os in valid_os:
            print(str(os.value) + ": " + os.name)
        os = int(input())
        #set OS from the input
        if os not in [os.value for os in valid_os]:
            print("Invalid OS")
            get_os()
        OS_USER = OS(os)
    return OS_USER


def create_variables():
    dict = {}
    variable: int = 1
    for i in range(0, N_ROW):
        for j in range(0, N_COL):
            for type in HC:
                if type not in [HC.N, HC.S, HC.E, HC.W]:
                    dict["_".join([str(type.value),str(i),str(j)])] = variable
                    variable += 1
    return dict


def get_variable(type, row: int, col: int):
    return VARIABLES["_".join([str(type.value), str(row), str(col)])]


def create_clauses():
    global CLAUSES
    #Clauses 1: Each cell has a type (EMPTY or WALL or GUARD_N...)
    clause = []
    for i in range(0, N_ROW):
        for j in range(0, N_COL):
            for type in HC:
                if type not in [HC.N, HC.S, HC.E, HC.W]:
                    clause.append(get_variable(type, i, j))
            CLAUSES.append(clause)
            clause = []

    #Clauses 2: Each cell has only one type
    for i in range(0, N_ROW):
        for j in range(0, N_COL):
            for type in HC:
                if type not in [HC.N, HC.S, HC.E, HC.W]:
                    for type2 in HC:
                        if type2 not in [HC.N, HC.S, HC.E, HC.W] and type != type2:
                            CLAUSES.append([-get_variable(type, i, j), -get_variable(type2, i, j)])
            
    #Clauses 3: The cell PIANO_WIRE / Target / Suit exists only one time
    clausePiano = []
    clauseSuit = []
    clauseTarget = []
    for i in range(0, N_ROW):
        for j in range(0, N_COL):
            clausePiano.append(-get_variable(HC.PIANO_WIRE, i, j))
            clauseSuit.append(-get_variable(HC.SUIT, i, j))
            clauseTarget.append(-get_variable(HC.TARGET, i, j))
    CLAUSES.append(clausePiano)
    CLAUSES.append(clauseSuit)
    CLAUSES.append(clauseTarget)

    #If the cell is a PIANO_WIRE/TARGET/SUIT, all the other cells are not a PIANO_WIRE/TARGET/SUIT
    for i in range(0, N_ROW):
        for j in range(0, N_COL):
            for k in range(i, N_ROW):
                for l in range(j, N_COL):
                    if i != k or j != l:
                        for type in [HC.PIANO_WIRE, HC.SUIT, HC.TARGET]:
                            CLAUSES.append([-get_variable(type, i, j), -get_variable(type, k, l)])


def add_clauses_map_test():
    global CLAUSES
    for key in complete_map_example:
        CLAUSES.append([get_variable(HC.EMPTY, key[0], key[1])])        


def write_dimacs_files():
    global CLAUSES
    check_current_directory()
    #Write the clauses in a file if exists replace it
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
    result = subprocess.run([gophersat_path, "gophersat/hitman.cnf"], capture_output=True, text=True)
    print(result.stdout)

def check_current_directory():
    if os.getcwd() != os.path.dirname(os.path.realpath(__file__)):
        print("Please execute this script from the root directory")
        exit(1)
        
if __name__ == "__main__":
    main()
