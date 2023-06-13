from hitman.hitman import HC, complete_map_example
import math
import heapq
from itertools import count

# globals
N_ROW = 7
N_COL = 7


class Case:
    def __init__(self, coordonnees):
        self.coordonnees = coordonnees
        self.g = 0  # Le coût depuis l'état initial
        self.h = 0  # L'estimation du coût minimal jusqu'a l'un des buts
        self.f = 0  # g + h
        self.parent = None

    def get_neighbors(self, map):
        neighbors = []
        x, y = self.coordonnees
        coord_voisins = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
        for coord in coord_voisins:
            # Vérifier si les coordonnées du voisin sont valides et que ce ne sont pas des murs
            if 0 <= coord[0] < N_COL and 0 <= coord[1] < N_ROW and map.get(coord) != HC.WALL:
                case = Case(coord)
                case.parent = self
                # case.g = self.g + 1
                neighbors.append(case)
        return (neighbors)


def a_star(map, start, goal):
    i = 0
    open_set = []  # Noeuds à explorer
    closed_set = set()  # Noeuds déjà explorés
    counter = count()
    heapq.heappush(open_set, (start.f, next(counter), start))
    while open_set:
        current = heapq.heappop(open_set)[2]

        if current.coordonnees == goal.coordonnees:
            # Retourner le chemin si nous avons atteint le nœud objectif
            path = []
            while current.parent:
                path.append(current.coordonnees)
                current = current.parent
            path.append(start.coordonnees)
            path.reverse()
            return path

        closed_set.add(current)

        for neighbor in current.get_neighbors(map):
            if neighbor in closed_set:
                continue

            if neighbor not in open_set:
                neighbor.parent = current
                neighbor.g = current.g + 1
                neighbor.h = neighbor.h + ((neighbor.coordonnees[0] - goal.coordonnees[0]) ** 2) + (
                    (neighbor.coordonnees[1] - goal.coordonnees[1]) ** 2)
                neighbor.f = neighbor.g + neighbor.h
                heapq.heappush(open_set, (neighbor.f, next(counter), neighbor))
    return None

def function_phase_2():
    
    # initialsie la case depart et les cases goal
    case_depart = Case((0, 0))
    for key, valeur in complete_map_example.items():
        if valeur == HC.PIANO_WIRE:
            case_corde = Case(key)
        if valeur == HC.TARGET:
            case_cible = Case(key)

    path = a_star(complete_map_example, case_depart, case_corde)
    print(path)
    path = a_star(complete_map_example, case_corde, case_cible)
    print(path)
    path = a_star(complete_map_example, case_cible, case_depart)
    print(path)


