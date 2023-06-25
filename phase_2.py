# ajout d'avancer sur la case quand je tue un civil et/ou un garde.
from copy import copy

from hitman.hitman import HC
import heapq
from itertools import count
from enum import Enum
import math
from pprint import pprint


# globals


class Action(Enum):
    AVANCER = "avancer"
    TUER_TARGET = "tuer_target"
    TUER = "tuer",
    RAMASSER_ARME = "ramasser_corde"
    RAMASSER_COSTUME = "ramasser_costume"
    METTRE_COSTUME = "mettre_costume"


class Case:
    def __init__(self, coordonnees, map=None):
        self.coordonnees = coordonnees
        self.g = 0  # Le coût depuis l'état initial
        self.h = 0  # L'estimation du coût minimal jusqu'a l'un des buts
        self.f = 0  # g + h
        self.parent = None
        self.action = None
        self.action_case = None
        self.map = map
        self.got_suit = False
        self.suit_on_hitman = False

    # to string
    def __repr__(self):
        return f"({self.coordonnees}, {self.f}, {self.action}, {self.action_case})"
    def __lt__(self, other):
        return self.f < other.f

    def __le__(self, other):
        return self.f <= other.f

    def __copy__(self):
        case = Case(self.coordonnees, self.map)
        case.g = self.g
        case.h = self.h
        case.parent = self.parent
        case.action = self.action
        case.action_case = self.action_case
        case.got_suit = self.got_suit
        case.suit_on_hitman = self.suit_on_hitman
        return case

    def get_neighbors(self):
        neighbors = []
        x, y = self.coordonnees
        coord_voisins = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
        for coord in coord_voisins:
            # Vérifier si les coordonnées du voisin sont valides et que ce ne sont pas des murs
            if 0 <= coord[0] < N_COL and 0 <= coord[1] < N_ROW and self.map.get(coord) != HC.WALL:
                case = Case(coord, self.map)
                case.g = self.g
                case.h = self.h
                case.parent = self
                neighbors.append(case)
        return (neighbors)


def a_star(map, start, goal):
    open_set = []  # Noeuds à explorer
    first_case = Case(start.coordonnees, copy_map(map))
    heapq.heappush(open_set, (start.f, first_case))
    # si i depasse 1000, alors cela retourne None, cela veut dire que le goal n'est pas atteignable
    while open_set:  # evite les boucles infinies
        current = heapq.heappop(open_set)[1]
        current_map = current.map
        if current.coordonnees == goal.coordonnees:
            if current_map[current.coordonnees] == HC.PIANO_WIRE:
                current.action = Action.RAMASSER_ARME
                temp_map = copy(current.map)
                temp_map[current.coordonnees] = HC.EMPTY
                current.map = temp_map
            if current_map[current.coordonnees] == HC.TARGET:
                current.action = Action.TUER_TARGET
            # Retourner le chemin si nous avons atteint le nœud objectif
            path = []
            while current.parent:
                path.append(current)
                current = current.parent
            path.append(start)
            path.reverse()
            return path

        for neighbor in current.get_neighbors():
            # on tue dans tout les cas mais on augmente l'heuristique, l'algo choisira tout seul
            map_temp = neighbor.map
            neighbor.got_suit = current.got_suit
            neighbor.suit_on_hitman = current.suit_on_hitman
            neighbor.parent = current

            if map_temp[neighbor.coordonnees] in [HC.CIVIL_E, HC.CIVIL_N, HC.CIVIL_S, HC.CIVIL_W, HC.GUARD_E,
                                                  HC.GUARD_N, HC.GUARD_S, HC.GUARD_W]:
                x, y = neighbor.parent.coordonnees
                x1, y1 = neighbor.coordonnees
                if ((y > y1) and map_temp[neighbor.coordonnees] not in [HC.CIVIL_N, HC.GUARD_N]) or (
                        (y1 > y) and map_temp[neighbor.coordonnees] not in [HC.CIVIL_S, HC.GUARD_S]) or (
                        (x > x1) and map_temp[neighbor.coordonnees] not in [HC.CIVIL_E, HC.GUARD_E]) or (
                        (x1 > x) and map_temp[neighbor.coordonnees] not in [HC.CIVIL_W, HC.GUARD_W]):
                    neighbor_ = copy(neighbor)
                    neighbor_.action = Action.TUER
                    neighbor_.action_case = neighbor.coordonnees
                    neighbor_.coordonnees = neighbor.parent.coordonnees  # on reste sur la meme case
                    neighbor_.h += 20  # penalité ajoutée au cout
                    neighbor_.map = copy(neighbor.map)
                    neighbor_.map[neighbor_.action_case] = HC.EMPTY
                    penalities_cases = get_penalties_guards(neighbor_.map) + get_penalties_civils(neighbor_.map)
                    for case in penalities_cases:
                        if neighbor_.coordonnees == case:
                            neighbor_.h += 100
                    add_to_neighbors(current, goal, map_temp, neighbor_, open_set)
            if map_temp[neighbor.coordonnees] == HC.TARGET and map_temp[neighbor.coordonnees] == goal.coordonnees:
                neighbor_ = copy(neighbor)
                neighbor_.action = Action.TUER_TARGET
                neighbor_.action_case = neighbor_.coordonnees
                neighbor_.map = copy(neighbor.map)
                neighbor_.map[neighbor_.action_case] = HC.EMPTY
                penalities_cases = get_penalties_guards(neighbor_.map) + get_penalties_civils(neighbor_.map)
                for case in penalities_cases:
                    if neighbor_.coordonnees == case:
                        neighbor_.h += 100
                add_to_neighbors(current, goal, map_temp, neighbor_, open_set)
            if map_temp[neighbor.coordonnees] in [HC.EMPTY, HC.PIANO_WIRE, HC.TARGET, HC.SUIT, HC.CIVIL_E, HC.CIVIL_W,
                                                  HC.CIVIL_N, HC.CIVIL_S]:
                neighbor_ = copy(neighbor)
                neighbor_.action = Action.AVANCER
                add_to_neighbors(current, goal, map_temp, neighbor_, open_set)

        map_temp = current.map
        if current.got_suit and not current.suit_on_hitman:
            neighbor = Case(current.coordonnees, current.map)
            neighbor.g = current.g
            neighbor.h = current.h
            neighbor.action = Action.METTRE_COSTUME
            neighbor.suit_on_hitman = True
            neighbor.got_suit = True
            neighbor.parent = current
            add_to_neighbors(current, goal, map_temp, neighbor, open_set)

        if map_temp[current.coordonnees] == HC.SUIT and not current.got_suit:
            neighbor = Case(current.coordonnees, copy_map(current.map))
            neighbor.g = current.g
            neighbor.h = current.h
            neighbor.action = Action.RAMASSER_COSTUME
            neighbor.got_suit = True
            neighbor.suit_on_hitman = False
            neighbor.map[neighbor.coordonnees] = HC.EMPTY
            neighbor.parent = current
            add_to_neighbors(current, goal, map_temp, neighbor, open_set)

    return None


def add_to_neighbors(current, goal, map_temp, neighbor, open_set):
    neighbor.parent = current
    # idée pour eviter les cases où regardent les gardes
    penalities_guards = get_penalties_guards(map_temp)
    for case in penalities_guards:
        if neighbor.coordonnees == case and not neighbor.suit_on_hitman and not neighbor.coordonnees in [HC.CIVIL_W,
                                                                                                         HC.CIVIL_E,
                                                                                                         HC.CIVIL_N,
                                                                                                         HC.CIVIL_S]:
            neighbor.h += 5
    penalities_cases = get_penalties_guards(map_temp) + get_penalties_civils(map_temp)
    for case in penalities_cases:
        if neighbor.coordonnees == case and neighbor.action == Action.METTRE_COSTUME:
            neighbor.h += 100
    neighbor.g += 1
    neighbor.h += math.sqrt((neighbor.coordonnees[0] - goal.coordonnees[0]) ** 2) + math.sqrt((
            (neighbor.coordonnees[1] - goal.coordonnees[1]) ** 2))
    neighbor.f = neighbor.g + neighbor.h
    heapq.heappush(open_set, (neighbor.f, neighbor))


def copy_map(map):
    new_map = {}
    for key, valeur in map.items():
        new_map[key] = valeur
    return new_map


def print_path(path):  # affiche le path avec les actions associées a réaliser dans chaque case
    print("\n")
    # mettre les actions aux cases associées
    if path != None:
        # je fais - 2 car je veux pas que l'avant derniere case prenne la valeur de la derniere
        for i in range(len(path) - 2):
            path[i].action = path[i + 1].action
            path[i].action_case = path[i + 1].action_case
        if path[len(path) - 1].action == Action.AVANCER:  # cas pour revenir a la case de depart, il faut s'arreter
            path[len(path) - 1].action = None
        path[
            len(path) - 2].action = Action.AVANCER  # l'avant dernière case du path sera forcement avancer avant le goal

        # path[len(path)-1].action = None
        # print mais provisoire car sert juste a observer pour le moment
        for case in path:
            print(case.coordonnees, end=' ')
            print(case.action)
        print()
    else:
        print("path is empty")
        return None


def get_penalties_guards(map):  # fonction qui recupere les case où nous sommes repérées par un garde, ce met a jour qu'une fois la map modifié du coup
    penalites = []
    for key, values in map.items():
        stop = False
        x, y = key[0], key[1]
        if values == HC.GUARD_S:
            for i in range(0, 3):
                if not stop:
                    if ((y - i) >= 0) and map[(x, (y - i))] not in [HC.WALL, HC.GUARD_N, HC.GUARD_E, HC.GUARD_W,
                                                                    HC.GUARD_S, HC.TARGET, HC.CIVIL_E, HC.CIVIL_W,
                                                                    HC.CIVIL_N, HC.CIVIL_S]:
                        penalites.append(Case((x, (y - i))).coordonnees)
                        if map[(x, (y - i))] != HC.EMPTY:
                            stop = True
        if values == HC.GUARD_N:
            for i in range(0, 3):
                if not stop:
                    if ((y + i) < N_ROW) and map[(x, (y + i))] not in [HC.WALL, HC.GUARD_N, HC.GUARD_E, HC.GUARD_W,
                                                                       HC.GUARD_S, HC.TARGET, HC.CIVIL_E, HC.CIVIL_W,
                                                                       HC.CIVIL_N, HC.CIVIL_S]:
                        penalites.append(Case((x, (y + i))).coordonnees)
                        if map[(x, (y + i))] != HC.EMPTY:
                            stop = True
        if values == HC.GUARD_E:
            for i in range(0, 3):
                if not stop:
                    if ((x + i) < N_COL) and map[(x + i, y)] not in [HC.WALL, HC.GUARD_N, HC.GUARD_E, HC.GUARD_W,
                                                                     HC.GUARD_S, HC.TARGET, HC.CIVIL_E, HC.CIVIL_W,
                                                                     HC.CIVIL_N, HC.CIVIL_S]:
                        penalites.append(Case((x + i, y)).coordonnees)
                        if map[(x + i, y)] != HC.EMPTY:
                            stop = True
        if values == HC.GUARD_W:
            for i in range(0, 3):
                if not stop:
                    if ((x - i) >= 0) and map[(x - i, y)] not in [HC.WALL, HC.GUARD_N, HC.GUARD_E, HC.GUARD_W,
                                                                  HC.GUARD_S, HC.TARGET, HC.CIVIL_E, HC.CIVIL_W,
                                                                  HC.CIVIL_N, HC.CIVIL_S]:
                        penalites.append(Case((x - i, y)).coordonnees)
                        if map[(x - i, y)] != HC.EMPTY:
                            stop = True
    return penalites


def get_penalties_civils(
        map):  # fonction qui recupere les case où nous sommes repérées par un garde, ce met a jour qu'une fois la map modifié du coup
    penalites = []
    for key, values in map.items():
        stop = False
        x, y = key[0], key[1]
        if values == HC.CIVIL_S:
            for i in range(0, 2):
                if not stop:
                    if ((y - i) >= 0) and map[(x, (y - i))] not in [HC.WALL, HC.GUARD_N, HC.GUARD_E, HC.GUARD_W,
                                                                    HC.GUARD_S, HC.TARGET, HC.CIVIL_E, HC.CIVIL_W,
                                                                    HC.CIVIL_N, HC.CIVIL_S]:
                        penalites.append(Case((x, (y - i))).coordonnees)
                        if map[(x, (y - i))] != HC.EMPTY:
                            stop = True
        if values == HC.CIVIL_N:
            for i in range(0, 2):
                if not stop:
                    if ((y + i) >= 0) and map[(x, (y + i))] not in [HC.WALL, HC.GUARD_N, HC.GUARD_E, HC.GUARD_W,
                                                                    HC.GUARD_S, HC.TARGET, HC.CIVIL_E, HC.CIVIL_W,
                                                                    HC.CIVIL_N, HC.CIVIL_S]:
                        penalites.append(Case((x, (y + i))).coordonnees)
                        if map[(x, (y + i))] != HC.EMPTY:
                            stop = True
        if values == HC.CIVIL_E:
            for i in range(0, 2):
                if not stop:
                    if ((x + i) < N_COL) and map[(x + i, y)] not in [HC.WALL, HC.GUARD_N, HC.GUARD_E, HC.GUARD_W,
                                                                     HC.GUARD_S, HC.TARGET, HC.CIVIL_E, HC.CIVIL_W,
                                                                     HC.CIVIL_N, HC.CIVIL_S]:
                        penalites.append(Case((x + i, y)).coordonnees)
                        if map[(x + i, y)] != HC.EMPTY:
                            stop = True
        if values == HC.CIVIL_W:
            for i in range(0, 2):
                if not stop:
                    if ((x - i) >= 0) and map[(x - i, y)] not in [HC.WALL, HC.GUARD_N, HC.GUARD_E, HC.GUARD_W,
                                                                  HC.GUARD_S, HC.TARGET, HC.CIVIL_E, HC.CIVIL_W,
                                                                  HC.CIVIL_N, HC.CIVIL_S]:
                        penalites.append(Case((x - i, y)).coordonnees)
                        if map[(x - i, y)] != HC.EMPTY:
                            stop = True
    return penalites


def get_guard(map):  # fonction qui recupere les coordonnees des gardes
    guard = []
    # ajouter coordonnées des civils et gardes
    for key, valeur in map.items():
        if "GUARD" in str(valeur):
            guard.append(key)
    return guard


def update_map(map,
               path):  # update de la map seulement a la fin de la premiere recherche, a modifier pour qu'on puisse mette a jour en direct
    for key, valeur in map.items():
        if valeur == HC.TARGET:
            case_cible = Case(key)
    for i in range(len(path)):
        if path[i].action == Action.TUER and path[i].coordonnees != case_cible.coordonnees:
            # Vérifier si la case suivante existe
            if i + 1 < len(path):
                next_case = path[i + 1]
                map[next_case.coordonnees] = HC.EMPTY
        elif path[i].action == Action.RAMASSER_ARME:
            map[path[i].coordonnees] = HC.EMPTY
        elif path[i].action == Action.TUER and path[i].coordonnees == case_cible.coordonnees:
            map[path[i].coordonnees] = HC.EMPTY

    return map


def phase2_run(hr, path, status, map):
    for i in range(len(path)):
        # trouver l'orientation but
        orientation = status["orientation"]
        position = status["position"]
        if i < len(path) - 1:
            x, y = position
            if path[i].action_case:
                x1, y1 = path[i].action_case
            else:
                x1, y1 = path[i + 1].coordonnees
            dx = x1 - x
            dy = y1 - y
            if dy > 0:
                if orientation == HC.E:
                    status = hr.turn_anti_clockwise()
                elif orientation == HC.S:
                    status = hr.turn_clockwise()
                    status = hr.turn_clockwise()
                elif orientation == HC.W:
                    status = hr.turn_clockwise()
            elif dy < 0:
                if orientation == HC.N:
                    status = hr.turn_clockwise()
                    status = hr.turn_clockwise()
                elif orientation == HC.E:
                    status = hr.turn_clockwise()
                elif orientation == HC.W:
                    status = hr.turn_anti_clockwise()

            print(orientation, dx, dy, path[i + 1].coordonnees)
            if dx > 0:
                if orientation == HC.N:
                    status = hr.turn_clockwise()
                elif orientation == HC.S:
                    status = hr.turn_anti_clockwise()
                elif orientation == HC.W:
                    status = hr.turn_clockwise()
                    status = hr.turn_clockwise()
            elif dx < 0:
                if orientation == HC.N:
                    status = hr.turn_anti_clockwise()
                elif orientation == HC.E:
                    status = hr.turn_clockwise()
                    status = hr.turn_clockwise()
                elif orientation == HC.S:
                    status = hr.turn_clockwise()

        # Maintenant faire l'action de la case

        if path[i].action == Action.AVANCER:
            status = hr.move()
            print(status)
        elif path[i].action == Action.RAMASSER_ARME:
            status = hr.take_weapon()
            print(status)
        elif path[i].action == Action.TUER_TARGET and map[path[i].coordonnees] == HC.TARGET and status[
            'is_target_down'] == False:
            status = hr.kill_target()
            print(status)
        elif path[i].action == Action.TUER and str(map[path[i].action_case]).startswith('HC.CIVIL'):
            status = hr.neutralize_civil()
            print(status)
        elif path[i].action == Action.TUER and str(map[path[i].action_case]).startswith('HC.GUARD'):
            status = hr.neutralize_guard()
            print(status)
        elif path[i].action == Action.RAMASSER_COSTUME:
            status = hr.take_suit()
            print(status)
        elif path[i].action == Action.METTRE_COSTUME:
            status = hr.put_on_suit()
            print(status)
    return status


def function_phase_2(HR, correct_map):
    global N_ROW, N_COL
    status = HR.start_phase2()
    N_ROW = status["m"]
    N_COL = status["n"]
    print(N_ROW, N_COL)
    # initialsie la case depart et les cases goal
    case_depart = Case((0, 0), copy_map(correct_map))
    for key, valeur in correct_map.items():
        if valeur == HC.PIANO_WIRE:
            case_corde = Case(key, correct_map)
        if valeur == HC.TARGET:
            case_cible = Case(key, correct_map)

    print("loading...")
    path = a_star(correct_map, case_depart, case_corde)
    print_path(path)
    status = phase2_run(HR, path, status, path[0].map)  # fonction qui appelle l'arbitre

    case_corde.map = copy_map(path[-1].map)
    case_corde.suit_on_hitman = path[-1].suit_on_hitman
    case_corde.got_suite = path[-1].got_suit
    print(case_corde.suit_on_hitman)
    print("loading...")
    path = a_star(copy(case_corde.map), case_corde, case_cible)
    print(path)
    print_path(path)
    print(path)
    status = phase2_run(HR, path, status, path[0].map)

    print("loading...")
    case_cible.map = copy_map(path[-1].map)
    case_cible.suit_on_hitman = path[-1].suit_on_hitman
    case_cible.got_suite = path[-1].got_suit
    path = a_star(copy_map(case_cible.map), case_cible, case_depart)
    print_path(path)
    phase2_run(HR, path, status, path[0].map )

    _, score, history = HR.end_phase2()
    pprint(history)
    print("Fin de la phase 2 : ")
    pprint(score)
