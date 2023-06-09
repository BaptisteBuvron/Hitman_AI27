from hitman.hitman import HC, complete_map_example

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


def a_star(map, debut, but):
    # initialisation des listes ouvertes et fermées
    open_list = []
    closed_list = []

    # Commencer avec la case de depart
    open_list.append(debut)

    while len(open_list) > 0:
        # Get the current node
        current_node = open_list[0]
        current_index = 0
        for index, item in enumerate(open_list):
            if item.f < current_node.f:
                current_node = item
                current_index = index
        # Pop current off open list, add to closed list
        open_list.pop(current_index)
        closed_list.append(current_node)
        # Found the goal
        if current_node.coordonnees == but.coordonnees:
            path = []
            current = current_node
            while current is not None:
                path.append(current.coordonnees)
                current = current.parent
            return path[::-1]  # Return reversed path
        # Generate children
        children = current_node.get_neighbors(map)

        for child in children:
            # Child is on the closed list
            for closed_child in closed_list:
                if child.coordonnees == closed_child.coordonnees:
                    continue
            # Create the f, g, and h values
            child.g = current_node.g + 1
            child.h = ((child.coordonnees[0] - but.coordonnees[0]) ** 2) + (
                    (child.coordonnees[1] - but.coordonnees[1]) ** 2)
            child.f = child.g + child.h
            # Child is already in the open list

            for open_node in open_list:
                if child.coordonnees == open_node.coordonnees and child.g > open_node.g:
                    continue

            # Add the child to the open list
            open_list.append(child)


def function_phase_2():
    # initialise une liste de type Case avec toutes les coordonnees présentes dans complete_map_example
    cases = []
    for key in complete_map_example.keys():
        cases.append(Case(key))
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


