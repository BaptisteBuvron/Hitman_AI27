from hitman.hitman import HC, complete_map_example
import heapq
from itertools import count
from enum import Enum
import math

# globals
N_ROW = 6
N_COL = 7

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
    while open_set and i < 10000:
        i = i + 1
        current = heapq.heappop(open_set)[2]

        if current.coordonnees == goal.coordonnees:
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
            if neighbor in closed_set: # A voir mais beaucoup moins performant sans
                continue
            if neighbor not in open_set:

                # si le voisin est un garde, alors on dit que l'action actuelle est de tuer et on augmente l'heurisitque de la case suivante
                if neighbor.coordonnees in get_civil_guard(map):
                    neighbor.action = Action.TUER  #  pour l'instant je mets dans neighbor car c'est plus simple et apres dans print_path je redecale les actions
                    neighbor.h += 6  # penalité ajoutée a l'heuristique (si je mets trop ca rame trop longtemps quand c'est un peu tricky
                if map[neighbor.coordonnees] == HC.TARGET:
                    neighbor.action = Action.TUER
                if map[neighbor.coordonnees] == HC.PIANO_WIRE:
                    neighbor.action = Action.RAMASSER_ARME
                if map[neighbor.coordonnees] == HC.EMPTY:
                    neighbor.action = Action.AVANCER

                neighbor.parent = current
                neighbor.g = current.g + 1

                # idée pour eviter les cases où regardent les gardes
                if neighbor.coordonnees in get_penalties(map):
                    neighbor.h += 6  # penalité ajoutée a l'heuristique (si je mets trop ca rame trop longtemps quand c'est un peu tricky

                neighbor.h += math.sqrt((neighbor.coordonnees[0] - goal.coordonnees[0]) ** 2) + math.sqrt((
                    (neighbor.coordonnees[1] - goal.coordonnees[1]) ** 2))
                neighbor.f = neighbor.g + neighbor.h
                heapq.heappush(open_set, (neighbor.f, next(counter), neighbor))
    return None
def print_path(path):   # affiche le path avec les actions associées a réaliser dans chaque case
    # mettre les actions aux cases associées
    if path != None:
        for i in range(len(path)-1):
            path[i].action = path[i+1].action
        path[len(path)-1].action = None
        # print mais provisoire car sert juste a observer pour le moment
        for case in path:
            print(case.coordonnees, end=' ')
            print(case.action, end=' ')
            print()
        print("\n")
    else:
        print("path is empty")
        return None

def get_penalties(map):     # fonction qui recupere les case où nous sommes repérées par un garde, ce met a jour qu'une fois la map modifié du coup
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

def get_civil_guard(map):       # fonction qui recupere les coordonnees des gardes et des civils
    civil_or_guard = []
    # ajouter coordonnées des civils et gardes
    for key, valeur in complete_map_example.items():
        if "GUARD" in str(valeur) or "CIVIL" in str(valeur):
            civil_or_guard.append(key)
    return civil_or_guard

def update_map(map, path):      #  update de la map seulement a la fin de la premiere recherche, a modifier pour qu'on puisse mette a jour en direct
    for i in range(len(path)):
        if path[i].action == Action.TUER:
            # Vérifier si la case suivante existe
            if i + 1 < len(path):
                next_case = path[i + 1]
                map[next_case.coordonnees] = HC.EMPTY
    return map
def function_phase_2():
    global complete_map_example
    # initialsie la case depart et les cases goal
    case_depart = Case((0, 0))
    for key, valeur in complete_map_example.items():
        if valeur == HC.PIANO_WIRE:
            case_corde = Case(key)
        if valeur == HC.TARGET:
            case_cible = Case(key)

    path = a_star(complete_map_example, case_depart, case_corde)
    print_path(path)
    complete_map_example = update_map(complete_map_example, path)

    path = a_star(complete_map_example, case_corde, case_cible)
    print_path(path)
    complete_map_example = update_map(complete_map_example, path)

    path = a_star(complete_map_example, case_cible, case_depart)
    print_path(path)
