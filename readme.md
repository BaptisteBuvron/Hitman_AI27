![Python Logo](https://www.python.org/static/community_logos/python-logo-master-v3-TM.png)
# Projet Hitman AI27

Ce projet est le projet final de l'UV AI27.

Membre du groupe:
- Baptiste BUVRON
- Axel PAPILLIER

# Hitman

Ce répertoire contient les éléments qui vous seront utiles pour votre projet. Un exemple d'utilisation vous est donné dans example_main.py. Il vous permet au travers d'une succession d'utilisation des méthodes de ```HitmanReferee``` d'avoir une illustration pour l'exemple donné dans le sujet. Pour vous en servir vous devrez importer ```HitmanReferee``` et ```HC``` dans votre projet.

## Types de base

```python
# Hitman constants
class HC(Enum):
    EMPTY = 1
    WALL = 2
    GUARD_N = 3
    GUARD_E = 4
    GUARD_S = 5
    GUARD_W = 6
    CIVIL_N = 7
    CIVIL_E = 8
    CIVIL_S = 9
    CIVIL_W = 10
    TARGET = 11
    SUIT = 12
    PIANO_WIRE = 13
    N = 14
    E = 15
    S = 16
    W = 17
```

Énumération contenant les types que peuvent prendre les différentes cases de la carte.

## Méthodes Phase 1

- `start_phase1()`
- `turn_clockwise()`
- `turn_anti_clockwise()`
- `move()`
- `send_content(map_info)`

Ces méthodes de ```HitmanReferee``` vont vous permettre de récupérer les différentes informations de la partie. 

### `start_phase1()`

Initialise la partie et vous renvoie l'état initial, sous forme de dictionnaire.

Exemple :
```python
{'civil_count': 3,
 'guard_count': 2,
 'hear': 0,
 'is_in_guard_range': False,
 'm': 6,
 'n': 7,
 'orientation': <HC.N: 14>,
 'penalties': 0,
 'phase': 1,
 'position': (0, 0),
 'status': 'OK',
 'vision': [((0, 1), <HC.EMPTY: 1>), ((0, 2), <HC.WALL: 2>)]}
```

### `turn_clockwise()`, `turn_anti_clockwise()`

Effectue une rotation horaire ou anti-horaire de Hitman et renvoie l'état du monde modifié par cette action, sous forme de dictionnaire.

Par exemple, si immédiatement après l'état initial nous appelons `turn_clockwise()` nous aurons alors :
```python
{'civil_count': 3,
 'guard_count': 2,
 'hear': 0,
 'is_in_guard_range': False,
 'm': 6,
 'n': 7,
 'orientation': <HC.E: 15>,
 'penalties': 1,
 'phase': 1,
 'position': (0, 0),
 'status': 'OK',
 'vision': [((1, 0), <HC.EMPTY: 1>), ((2, 0), <HC.WALL: 2>)]}
```

Vous noterez que le champ `'penalties'`  a augmenté de 1, étant donné que nous avons fait une action. (cf. décompte des points)

### `move()`

Effectue un pas vers la direction dans laquelle Hitman est orienté (HC.N, HC.E, HC.S, HC.W) et renvoie l'état du monde modifié par cette action, sous forme de dictionnaire. 

Attention, si l'action demandée n'est pas valide le champs `'status'` ne sera plus à `'OK'` et l'action ne sera pas effectuée. Les pénalités sont bien mises à jour.

### `send_content(map_info)`

Cette méthode vous permet de tester si vous avez bien obtenu la bonne carte. L'argument `map_info` est de type `Dict[Tuple[int, int], HC]`. C'est donc un dictionnaire qui associera à chaque paires de coordonnées $(x, y)$ un contenu de case.

Cette méthode renvoie la valeur `True` si le dictionnaire contient exactement toutes les cases de la carte avec les bons contenus, `False` sinon.
