``# Modélisation SAT de la Phase 1

Pour modéliser notre problème en SAT, nous avons créer une classe `ClausesManager` qui écrit au fur et à mesure les clauses dans un fichier `clauses.txt`. Cette classe permet de simplifier l'écriture des clauses pour pouvoir les utiliser dans le solveur SAT.

## Variables

Au début du programme à partir du status initial, nous créons les variables suivantes :

- `GUARD_N_X_Y` : il y a un garde orienté au Nord en position (X,Y)
- `GUARD_E_X_Y` : il y a un garde orienté à l'Est en position (X,Y)
- `GUARD_S_X_Y` : il y a un garde orienté au Sud en position (X,Y)
- `GUARD_W_X_Y` : il y a un garde orienté à l'Ouest en position (X,Y)
- `CIVIL_N_X_Y` : il y a un civil orienté au Nord en position (X,Y)
- `CIVIL_E_X_Y` : il y a un civil orienté à l'Est en position (X,Y)
- `CIVIL_S_X_Y` : il y a un civil orienté au Sud en position (X,Y)
- `CIVIL_W_X_Y` : il y a un civil orienté à l'Ouest en position (X,Y)
- `TARGET_X_Y` : il y a une cible en position (X,Y)
- `SUIT_X_Y` : il y a un costume en position (X,Y)
- `PIANO_WIRE_X_Y` : il y a un fil de piano en position (X,Y)
- `WALL_X_Y` : il y a un mur en position (X,Y)
- `EMPTY_X_Y` : il y a une case vide en position (X,Y)

Nous avons également ajouté 3 variables afin de limiter le nombre de clauses:

- `GUARD_X_Y` : il y a un garde en position (X,Y)
- `CIVIL_X_Y`: il y a un civil en position (X,Y)
- `LISTENING_X_Y`: il est possible q'un garde ou q'un civil ai été entendu en (X,Y)


## Clauses

### Clauses de base

Ensuite avant le début de l'exploration, nous ajoutons les clauses de base qui sont les suivantes :

#### Chaque case à une valeur

`GUARD_N_X_Y` OR `GUARD_E_X_Y` OR `GUARD_S_X_Y` OR `GUARD_W_X_Y` OR `CIVIL_N_X_Y` OR `CIVIL_E_X_Y` OR `CIVIL_S_X_Y` OR `CIVIL_W_X_Y` OR `TARGET_X_Y` OR `SUIT_X_Y` OR `PIANO_WIRE_X_Y` OR `WALL_X_Y` OR `EMPTY_X_Y`

#### Chaque case à une seule valeur

Exemple pour la case GUARD_N_X_Y :

`GUARD_N_X_Y` -> ( ¬`GUARD_E_X_Y` AND ¬`GUARD_S_X_Y` AND ¬`GUARD_W_X_Y` AND ¬`CIVIL_N_X_Y` AND ¬`CIVIL_E_X_Y` AND ¬`CIVIL_S_X_Y` AND ¬`CIVIL_W_X_Y` AND ¬`TARGET_X_Y` AND ¬`SUIT_X_Y` AND ¬`PIANO_WIRE_X_Y` AND ¬`WALL_X_Y` AND ¬`EMPTY_X_Y`)

On transforme l'implication:

¬`GUARD_N_X_Y` OR ( ¬`GUARD_E_X_Y` AND ¬`GUARD_S_X_Y` AND ¬`GUARD_W_X_Y` AND ¬`CIVIL_N_X_Y` AND ¬`CIVIL_E_X_Y` AND ¬`CIVIL_S_X_Y` AND ¬`CIVIL_W_X_Y` AND ¬`TARGET_X_Y` AND ¬`SUIT_X_Y` AND ¬`PIANO_WIRE_X_Y` AND ¬`WALL_X_Y` AND ¬`EMPTY_X_Y`)

On distribue pour convertir en CNF

(¬`GUARD_N_X_Y` OR ¬`GUARD_E_X_Y`) AND (¬`GUARD_N_X_Y` OR ¬`GUARD_S_X_Y`) AND (¬`GUARD_N_X_Y` OR ¬`GUARD_W_X_Y`) AND (¬`GUARD_N_X_Y` OR ¬`CIVIL_N_X_Y`) AND (¬`GUARD_N_X_Y` OR ¬`CIVIL_E_X_Y`) AND (¬`GUARD_N_X_Y` OR ¬`CIVIL_S_X_Y`) AND (¬`GUARD_N_X_Y` OR ¬`CIVIL_W_X_Y`) AND (¬`GUARD_N_X_Y` OR ¬`TARGET_X_Y`) AND (¬`GUARD_N_X_Y` OR ¬`SUIT_X_Y`) AND (¬`GUARD_N_X_Y` OR ¬`PIANO_WIRE_X_Y`) AND (¬`GUARD_N_X_Y` OR ¬`WALL_X_Y`) AND (¬`GUARD_N_X_Y` OR ¬`EMPTY_X_Y`)

#### Les types TARGET_X_Y, PIANO_WIRE_X_Y et SUIT_X_Y sont uniques

Exemple pour la case TARGET_X_Y :

¬`TARGET_0_0` OR ¬`TARGET_0_1` OR ¬`TARGET_0_2` OR ¬`TARGET_1_0` OR ¬`TARGET_1_1` OR ¬`TARGET_1_2` OR ¬`TARGET_2_0` OR ¬`TARGET_2_1` OR ¬`TARGET_2_2` ...

Si une case est une TARGET alors toutes les autres cases ne sont pas des TARGET

`TARGET_0_0` -> (¬`TARGET_0_1` AND ¬`TARGET_0_2` AND ¬`TARGET_1_0` AND ¬`TARGET_1_1` AND ¬`TARGET_1_2` AND ¬`TARGET_2_0` AND ¬`TARGET_2_1` AND ¬`TARGET_2_2` ...)

On transforme l'implication:

¬`TARGET_0_0` OR (¬`TARGET_0_1` AND ¬`TARGET_0_2` AND ¬`TARGET_1_0` AND ¬`TARGET_1_1` AND ¬`TARGET_1_2` AND ¬`TARGET_2_0` AND ¬`TARGET_2_1` AND ¬`TARGET_2_2` ...)

On distribue pour convertir en CNF

(¬`TARGET_0_0` OR ¬`TARGET_0_1`) AND (¬`TARGET_0_0` OR ¬`TARGET_0_2`) AND (¬`TARGET_0_0` OR ¬`TARGET_1_0`) AND (¬`TARGET_0_0` OR ¬`TARGET_1_1`) AND (¬`TARGET_0_0` OR ¬`TARGET_1_2`) AND (¬`TARGET_0_0` OR ¬`TARGET_2_0`) AND (¬`TARGET_0_0` OR ¬`TARGET_2_1`) AND (¬`TARGET_0_0` OR ¬`TARGET_2_2`) AND ...

On réalise les mêmes opérations pour les cases PIANO_WIRE_X_Y et SUIT_X_Y

#### Un GUARD_X_Y est équivalent à (GUARD_N_X_Y`OR`GUARD_E_X_Y`OR`GUARD_S_X_Y`OR`GUARD_W_X_Y`)

`GUARD_X_Y` <-> ( `GUARD_E_X_Y` OR `GUARD_S_X_Y` OR `GUARD_W_X_Y` OR `GUARD_N_X_Y`)

On transforme l'équivalence:

`GUARD_X_Y` -> ( `GUARD_E_X_Y` OR `GUARD_S_X_Y` OR `GUARD_W_X_Y` OR `GUARD_N_X_Y`)
( `GUARD_E_X_Y` OR `GUARD_S_X_Y` OR `GUARD_W_X_Y` OR `GUARD_N_X_Y`) -> `GUARD_X_Y`



On transforme les implications:

¬`GUARD_X_Y` OR ( `GUARD_E_X_Y` OR `GUARD_S_X_Y` OR `GUARD_W_X_Y` OR `GUARD_N_X_Y`)
( `GUARD_E_X_Y` OR `GUARD_S_X_Y` OR `GUARD_W_X_Y` OR `GUARD_N_X_Y`) OR ¬`GUARD_X_Y`

On distribue pour convertir en CNF

(¬`GUARD_X_Y` OR `GUARD_E_X_Y`) AND (¬`GUARD_X_Y` OR `GUARD_S_X_Y`) AND (¬`GUARD_X_Y` OR `GUARD_W_X_Y`) AND (¬`GUARD_X_Y` OR `GUARD_N_X_Y`)

#### Un CIVIL_X_Y est équivalent à (CIVIL_N_X_Y`OR`CIVIL_E_X_Y`OR`CIVIL_S_X_Y`OR`CIVIL_W_X_Y`)

`CIVIL_X_Y` <-> ( `CIVIL_E_X_Y` OR `CIVIL_S_X_Y` OR `CIVIL_W_X_Y` OR `CIVIL_N_X_Y`)

On transforme l'équivalence:

`CIVIL_X_Y` -> ( `CIVIL_E_X_Y` OR `CIVIL_S_X_Y` OR `CIVIL_W_X_Y` OR `CIVIL_N_X_Y`)
( `CIVIL_E_X_Y` OR `CIVIL_S_X_Y` OR `CIVIL_W_X_Y` OR `CIVIL_N_X_Y`) -> `CIVIL_X_Y`


On transforme l'implication:

¬`CIVIL_X_Y` OR ( `CIVIL_E_X_Y` OR `CIVIL_S_X_Y` OR `CIVIL_W_X_Y` OR `CIVIL_N_X_Y`)
¬( `CIVIL_E_X_Y` OR `CIVIL_S_X_Y` OR `CIVIL_W_X_Y` OR `CIVIL_N_X_Y`) OR `CIVIL_X_Y`

On distribue pour convertir en CNF

(¬`CIVIL_X_Y` OR `CIVIL_E_X_Y`) AND (¬`CIVIL_X_Y` OR `CIVIL_S_X_Y`) AND (¬`CIVIL_X_Y` OR `CIVIL_W_X_Y`) AND (¬`CIVIL_X_Y` OR `CIVIL_N_X_Y`)
(¬`CIVIL_E_X_Y` OR `CIVIL_X_Y`) AND (¬`CIVIL_S_X_Y` OR `CIVIL_X_Y`) AND (¬`CIVIL_W_X_Y` OR `CIVIL_X_Y`) AND (¬`CIVIL_N_X_Y` OR `CIVIL_X_Y`)

#### Un LISTENING_X_Y implique (GUARD_X_Y`OR`CIVIL_X_Y)

`LISTENING_X_Y` -> ( `GUARD_X_Y` OR `CIVIL_X_Y`)

On transforme l'implication:

¬`LISTENING_X_Y` OR ( `GUARD_X_Y` OR `CIVIL_X_Y`)

On distribue pour convertir en CNF

(¬`LISTENING_X_Y` OR `GUARD_X_Y`) AND (¬`LISTENING_X_Y` OR `CIVIL_X_Y`)


