# ajout d'avancer sur la case quand je tue un civil et/ou un garde.

from hitman.hitman import HC, complete_map_example, HitmanReferee
import heapq
from itertools import count
from enum import Enum
import math
from pprint import pprint


# globals


class Action(Enum):
    AVANCER = "avancer"
    TUER = "tuer"
    RAMASSER_ARME = "ramassaer_corde"


class Case:
    def __init__(self, coordonnees):
        self.coordonnees = coordonnees
        self.g = 0  # Le coût depuis l'état initial
        self.h = 0  # L'estimation du coût minimal jusqu'a l'un des buts
        self.f = 0  # g + h
        self.parent = None
        self.action = None
        self.map = None

    def get_neighbors(self, map):
        neighbors = []
        x, y = self.coordonnees
        coord_voisins = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
        for coord in coord_voisins:
            # Vérifier si les coordonnées du voisin sont valides et que ce ne sont pas des murs
            if 0 <= coord[0] < N_COL and 0 <= coord[1] < N_ROW and map.get(coord) != HC.WALL:
                case = Case(coord)
                case.parent = self
                neighbors.append(case)
        return (neighbors)


def a_star(map, start, goal):
    open_set = []  # Noeuds à explorer
    i = 0
    closed_set = set()  # Noeuds déjà explorés
    counter = count()
    heapq.heappush(open_set, (start.f, next(counter), start))
    # si i depasse 1000, alors cela retourne None, cela veut dire que le goal n'est pas atteignable
    while open_set and i < 10000000:  # evite les boucles infinies
        i = i + 1
        current = heapq.heappop(open_set)[2]

        current.map = map
        if current.coordonnees == goal.coordonnees:
            if map[current.coordonnees] == HC.PIANO_WIRE:
                current.action = Action.RAMASSER_ARME
            if map[current.coordonnees] == HC.TARGET:
                current.action = Action.TUER
            # Retourner le chemin si nous avons atteint le nœud objectif
            path = []
            while current.parent:
                path.append(current)
                current = current.parent
            path.append(start)
            path.reverse()
            return path

        closed_set.add(current)

        for neighbor in current.get_neighbors(map):
            if neighbor in closed_set:  # A voir mais beaucoup moins performant sans
                continue
            if neighbor not in open_set:

                # on tue dans tout les cas mais on augmente l'heuristique, l'algo choisira tout seul
                if neighbor.coordonnees in get_civil_guard(map):
                    neighbor.action = Action.TUER  # pour l'instant je mets dans neighbor car c'est plus simple et apres dans print_path je redecale les actions
                    neighbor.h += 6  # penalité ajoutée a l'heuristique (si je mets genre +10 ca rame trop longtemps quand la map devient un peu complexe)
                if map[neighbor.coordonnees] == HC.TARGET:
                    neighbor.action = Action.TUER
                if map[neighbor.coordonnees] == HC.EMPTY or map[neighbor.coordonnees] == HC.PIANO_WIRE:
                    neighbor.action = Action.AVANCER

                neighbor.parent = current
                neighbor.map = neighbor.parent.map
                neighbor.g = current.g + 1

                # idée pour eviter les cases où regardent les gardes
                if neighbor.coordonnees in get_penalties(map):
                    neighbor.h += 6  # penalité ajoutée a l'heuristique (si je mets genre +10 ca rame trop longtemps quand la map devient un peu complexe)

                neighbor.h += math.sqrt((neighbor.coordonnees[0] - goal.coordonnees[0]) ** 2) + math.sqrt((
                        (neighbor.coordonnees[1] - goal.coordonnees[1]) ** 2))
                neighbor.f = neighbor.g + neighbor.h
                heapq.heappush(open_set, (neighbor.f, next(counter), neighbor))
    return None


def print_path(path):  # affiche le path avec les actions associées a réaliser dans chaque case
    print("\n")
    # mettre les actions aux cases associées
    if path != None:
        # je fais - 2 car je veux pas que l'avant derniere case prenne la valeur de la derniere
        for i in range(len(path) - 2):
            path[i].action = path[i + 1].action
        if path[len(path) - 1].action == Action.AVANCER:
            path[len(path) - 1].action = None
        # path[len(path)-1].action = None
        # print mais provisoire car sert juste a observer pour le moment
        for case in path:
            print(case.coordonnees, end=' ')
            print(case.action, end='  ')
            print(case.map)
        print()
    else:
        print("path is empty")
        return None


def get_penalties(
        map):  # fonction qui recupere les case où nous sommes repérées par un garde, ce met a jour qu'une fois la map modifié du coup
    penalites = []
    for key, values in complete_map_example.items():
        if values == HC.GUARD_S:
            x, y = key[0], key[1]
            penalites.append(Case((x, (y - 1))).coordonnees)
            penalites.append(Case((x, (y - 2))).coordonnees)
        if values == HC.GUARD_N:
            x, y = key[0], key[1]
            penalites.append(Case((x, (y + 1))).coordonnees)
            penalites.append(Case((x, (y + 2))).coordonnees)
        if values == HC.GUARD_E:
            x, y = key[0], key[1]
            penalites.append(Case(((x + 1), y)).coordonnees)
            penalites.append(Case(((x + 2), y)).coordonnees)
        if values == HC.GUARD_W:
            x, y = key[0], key[1]
            penalites.append(Case(((x - 1), y)).coordonnees)
            penalites.append(Case(((x - 2), y)).coordonnees)
        return penalites


def get_civil_guard(map):  # fonction qui recupere les coordonnees des gardes et des civils
    civil_or_guard = []
    # ajouter coordonnées des civils et gardes
    for key, valeur in complete_map_example.items():
        if "GUARD" in str(valeur) or "CIVIL" in str(valeur):
            civil_or_guard.append(key)
    return civil_or_guard


def update_map(map,
               path):  # update de la map seulement a la fin de la premiere recherche, a modifier pour qu'on puisse mette a jour en direct
    for i in range(len(path)):
        if path[i].action == Action.TUER:
            # Vérifier si la case suivante existe
            if i + 1 < len(path):
                next_case = path[i + 1]
                map[next_case.coordonnees] = HC.EMPTY

    return map


def phase2_run(hr, path, status, map):
    for i in range(len(path)):
        # trouver l'orientation but
        orientation = status["orientation"].value
        if i < len(path) - 1:
            x, y = path[i].coordonnees
            x1, y1 = path[i + 1].coordonnees
            if x > x1:
                orientation_but = 17  # Ouest
            elif x < x1:
                orientation_but = 15  # Est
            elif y > y1:
                orientation_but = 16  # Sud
            elif y < y1:
                orientation_but = 14  # Nord

            if orientation - orientation_but == -3:
                status = hr.turn_anti_clockwise()
            elif orientation - orientation_but == -2:
                status = hr.turn_anti_clockwise()
                status = hr.turn_anti_clockwise()
            elif orientation - orientation_but == -1:
                status = hr.turn_clockwise()
            elif orientation - orientation_but == 1:
                status = hr.turn_anti_clockwise()
            elif orientation - orientation_but == 2:
                status = hr.turn_anti_clockwise()
                status = hr.turn_anti_clockwise()
            elif orientation - orientation_but == 3:
                status = hr.turn_clockwise()

        # Maintenant faire l'action de la case
        if path[i].action == Action.AVANCER:
            status = hr.move()
            print(status)
        elif path[i].action == Action.RAMASSER_ARME:
            status = hr.take_weapon()
            print(status)
        elif path[i].action == Action.TUER and map[path[i].coordonnees] == HC.TARGET:
            status = hr.kill_target()
            print(status)
        elif path[i].action == Action.TUER and str(map[path[i + 1].coordonnees]).startswith('HC.CIVIL'):
            status = hr.neutralize_civil()
            print(status)
            status = hr.move()
            print(status)
        elif path[i].action == Action.TUER and str(map[path[i + 1].coordonnees]).startswith('HC.GUARD'):
            status = hr.neutralize_guard()
            print(status)
            status = hr.move()
            print(status)
    return status


def function_phase_2():
    global complete_map_example, N_ROW, N_COL
    hr = HitmanReferee()
    status = hr.start_phase2()
    N_ROW = status["m"]
    N_COL = status["n"]

    # initialsie la case depart et les cases goal
    case_depart = Case((0, 0))
    for key, valeur in complete_map_example.items():
        if valeur == HC.PIANO_WIRE:
            case_corde = Case(key)
        if valeur == HC.TARGET:
            case_cible = Case(key)

    path = a_star(complete_map_example, case_depart, case_corde)
    print_path(path)
    status = phase2_run(hr, path, status, complete_map_example)  # fonction qui appelle l'arbitre
    complete_map_example = update_map(complete_map_example, path)  # modification que à la fin de la phase (pas opti)

    path = a_star(complete_map_example, case_corde, case_cible)
    print_path(path)
    status = phase2_run(hr, path, status, complete_map_example)
    complete_map_example = update_map(complete_map_example, path)  # modification que à la fin de la phase (pas opti)

    path = a_star(complete_map_example, case_cible, case_depart)
    print_path(path)
    phase2_run(hr, path, status, complete_map_example)

    _, score, history = hr.end_phase2()
    pprint(score)
    pprint(history)


