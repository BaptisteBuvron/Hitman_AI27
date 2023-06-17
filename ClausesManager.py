import itertools
import os
import subprocess
from copy import copy
from enum import Enum
from pprint import pprint
from typing import List

from sympy import symbols, to_cnf

from hitman.hitman import HC
from movement import move_forward, is_inside_room, opposite_orientation_guard
from utils import OS


class Type(Enum):
    GUARD = 18
    CIVIL = 19

class ClausesManager:

    all_types = [HC.GUARD_E, HC.GUARD_N, HC.GUARD_S, HC.GUARD_W, HC.CIVIL_E, HC.CIVIL_N, HC.CIVIL_S, HC.CIVIL_W, HC.TARGET, HC.SUIT, HC.PIANO_WIRE, HC.EMPTY, HC.WALL, Type.GUARD, Type.CIVIL]

    def __init__(self, N_ROW: int, N_COL: int, N_GUARDS: int, N_CIVILS: int):
        self.visited = set()
        self.clauses = []
        self.variables = {}
        self.os_users = OS.none
        self.N_ROW = N_ROW
        self.N_COL = N_COL
        self.N_GUARDS = N_GUARDS
        self.N_CIVILS = N_CIVILS
        self.create_variables()
        self.create_clauses()

    def create_variables(self):
        self.variables = {}
        variable: int = 1
        for i in range(0, self.N_COL):
            for j in range(0, self.N_ROW):
                for type in HC:
                    if type not in [HC.N, HC.S, HC.E, HC.W]:
                        # I = row, J = COL
                        self.variables["_".join([str(type.value), str(i), str(j)])] = variable
                        variable += 1
                for type in Type:
                    self.variables["_".join([str(type.value), str(i), str(j)])] = variable
                    variable += 1

    def get_variable(self, type, row: int, col: int):
        return self.variables["_".join([str(type.value), str(row), str(col)])]

    def create_clauses(self):
        # Clauses 1: Each cell has a type (EMPTY or WALL or GUARD_N...)
        clause = []
        for i in range(0, self.N_COL):
            for j in range(0, self.N_ROW):
                for type in self.all_types:
                    clause.append(self.get_variable(type, i, j))
                self.clauses.append(clause)
                clause = []

        # Clauses 2: Each cell has only one type
        for i in range(0, self.N_COL):
            for j in range(0, self.N_ROW):
                for type in HC:
                    if type not in [HC.N, HC.S, HC.E, HC.W]:
                        for type2 in HC:
                            if type2 not in [HC.N, HC.S, HC.E, HC.W] and type != type2:
                                self.clauses.append(
                                    [-self.get_variable(type, i, j), -self.get_variable(type2, i, j)]
                                )

        # Clauses 3: The cell PIANO_WIRE / Target / Suit exists only one time
        clausePiano = []
        clauseSuit = []
        clauseTarget = []
        for i in range(0, self.N_COL):
            for j in range(0, self.N_ROW):
                clausePiano.append(-self.get_variable(HC.PIANO_WIRE, i, j))
                clauseSuit.append(-self.get_variable(HC.SUIT, i, j))
                clauseTarget.append(-self.get_variable(HC.TARGET, i, j))
        self.clauses.append(clausePiano)
        self.clauses.append(clauseSuit)
        self.clauses.append(clauseTarget)

        # If the cell is a PIANO_WIRE/TARGET/SUIT, all the other cells are not a PIANO_WIRE/TARGET/SUIT
        for i in range(0, self.N_COL):
            for j in range(0, self.N_ROW):
                for k in range(i, self.N_COL):
                    for l in range(j, self.N_ROW):
                        if i != k or j != l:
                            for type in [HC.PIANO_WIRE, HC.SUIT, HC.TARGET]:
                                self.clauses.append(
                                    [-self.get_variable(type, i, j), -self.get_variable(type, k, l)]
                                )


        #If a cell is a GUARD, the cell is GUARD_N, GUARD_S, GUARD_E or GUARD_W
        for i in range(0, self.N_COL):
            for j in range(0, self.N_ROW):
                tempClause = []
                tempClause.append(-self.get_variable(Type.GUARD, i, j))
                for type in [HC.GUARD_N, HC.GUARD_S, HC.GUARD_E, HC.GUARD_W]:
                    tempClause.append(-self.get_variable(type, i, j))
                self.clauses.append(tempClause)

        #If a cell is a CIVIL, the cell is CIVIL_N, CIVIL_S, CIVIL_E or CIVIL_W
        for i in range(0, self.N_COL):
            for j in range(0, self.N_ROW):
                tempClause = []
                tempClause.append(-self.get_variable(Type.CIVIL, i, j))
                for type in [HC.CIVIL_N, HC.CIVIL_S, HC.CIVIL_E, HC.CIVIL_W]:
                    tempClause.append(-self.get_variable(type, i, j))
                self.clauses.append(tempClause)

        #If a cell is a CIVIL_N or CIVIL_S or CIVIL_E or CIVIL_W, the cell is a CIVIL
        for i in range(0, self.N_COL):
            for j in range(0, self.N_ROW):
                for type in [HC.CIVIL_N, HC.CIVIL_S, HC.CIVIL_E, HC.CIVIL_W]:
                    self.clauses.append([self.get_variable(Type.CIVIL, i, j), -self.get_variable(type, i, j)])

        #If a cell is a GUARD_N or GUARD_S or GUARD_E or GUARD_W, the cell is a GUARD
        for i in range(0, self.N_COL):
            for j in range(0, self.N_ROW):
                for type in [HC.GUARD_N, HC.GUARD_S, HC.GUARD_E, HC.GUARD_W]:
                    self.clauses.append([self.get_variable(Type.GUARD, i, j), -self.get_variable(type, i, j)])

    def create_clauses_max_type(self, positions: List, types: List, max: int, ):
        # Il y a exactement 2 guards test array 3*3
        # get all values of dict
        values = list(self.variables.values())
        ls = symbols(" ".join([str(i) for i in values]))
        combinations = list(itertools.combinations(positions, max))
        if len(combinations) <= 1:
            return
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
                    clause.append(-self.get_variable(type, i[0], i[1]))
                dnf.append(clause)
            clause = []
            for j in other:
                for type in types:
                    clause.append(-self.get_variable(type, j[0], j[1]))
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
                self.clauses.append(clause)

    def analyse_status(self, status, room):
        pprint(status)
        # From the vision of the hitman, we can see the type of the 2 cells in front of him
        for vision in status["vision"]:
            # TODO Add unsafe cells (gards, walls)
            if room[self.N_ROW - 1 - int(vision[0][1])][int(vision[0][0])] == 0:
                # (0,0) is the bottom left corner
                room[self.N_ROW - 1 - int(vision[0][1])][int(vision[0][0])] = HC(vision[1])
                self.clauses.append(
                    [self.get_variable(HC(vision[1]), int(vision[0][0]), int(vision[0][1]))]
                )
                if HC(vision[1]) == HC.WALL:
                    # TODO Add blocked cells
                    pass

        if status["is_in_guard_range"]:
            clauses = []
            for orientation in [HC.N, HC.S, HC.E, HC.W]:
                for step in range(1, 3):
                    pos = move_forward(status["position"], orientation, step)
                    if is_inside_room(pos, self.N_ROW, self.N_COL):
                        clauses.append(self.get_variable(opposite_orientation_guard(orientation), pos[0], pos[1]))
            self.clauses.append(clauses)
            #self.deduct(room)
        else:
            for orientation in [HC.N, HC.S, HC.E, HC.W]:
                for step in range(1, 3):
                    pos = move_forward(status["position"], orientation, step)
                    if is_inside_room(pos, self.N_ROW, self.N_COL):
                        self.clauses.append([-self.get_variable(opposite_orientation_guard(orientation), pos[0], pos[1])])

        if status["hear"] != 0:
            if status["position"] not in self.visited:
                # Il y a x gardes ou un invités dans une des 2 cases autour de nous
                positions = self.get_positions_around(status["position"], 2)
                # remove the known cells
                positions = [position for position in positions if
                             room[self.N_ROW - 1 - int(position[1])][int(position[0])] not in [HC.WALL, HC.EMPTY,
                                                                                               HC.TARGET,
                                                                                               HC.PIANO_WIRE, HC.SUIT]]

                #self.create_clauses_max_type(positions,[Type.GUARD, Type.CIVIL], status["hear"])
                #self.visited.add(status["position"])
                pass
        else:
            # Vérifier combien de garde ou de civils qui ne sont pas dans la zone d'écoute, si la soustraction est en dessous de 5 ajouter les clauses.
            pass
        for i in range(self.N_ROW):
            for j in range(self.N_COL):
                longueur = 15
                print(room[i][j], end=" " * (longueur - len(str(room[i][j]))))
            print()
        pass

    def write_dimacs_files(self, clauses):
        self.check_current_directory()
        # Write the clauses in a file if exists replace it
        with open("gophersat/hitman.cnf", "w") as f:
            f.write("p cnf " + str(len(self.variables)) + " " + str(len(clauses)) + "\n")
            for clause in clauses:
                f.write(" ".join([str(x) for x in clause]) + " 0\n")
        pass

    def check_current_directory(self):
        if os.getcwd() != os.path.dirname(os.path.realpath(__file__)):
            print("Please execute this script from the root directory")
            exit(1)

    def execute_gophersat(self):
        self.check_current_directory()
        os_user = self.get_os()
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
        if result.stdout.find("s SATISFIABLE") != -1:
            return True
        return False

    def get_os(self):
        if self.os_users == OS.none:
            print("What OS are you using?")
            valid_os = [os for os in OS if os != OS.none]
            for os in valid_os:
                print(str(os.value) + ": " + os.name)
            os = int(input())
            # set OS from the input
            if os not in [os.value for os in valid_os]:
                print("Invalid OS")
                self.get_os()
            self.os_users = OS(os)
        return self.os_users

    def get_positions_around(self, position, radius):
        positions = []
        for i in range(-radius, radius + 1):
            for j in range(-radius, radius + 1):
                if is_inside_room((position[0] + i, position[1] + j), self.N_ROW, self.N_COL):
                    positions.append((position[0] + i, position[1] + j))
        return positions

    def deduct(self, room):
        print("Start deduction")
        for i in range(0, self.N_COL):
            for j in range(0, self.N_ROW):
                if room[self.N_ROW - 1 - j][i] == 0:
                    for type in self.all_types:
                            clauses_temp = copy(self.clauses)
                            clauses_temp.append([-self.get_variable(type, i, j)])
                            self.write_dimacs_files(clauses_temp)
                            if not self.execute_gophersat():
                                print("Found a solution : " + str(type) + " at " + str(i) + " " + str(j))
                                if type not in [Type.GUARD, Type.CIVIL]:
                                    room[self.N_ROW - 1 - j][i] = type
                                    self.clauses.append([self.get_variable(type, i, j)])
        print("End deduction")
