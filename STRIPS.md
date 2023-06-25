## STRIPS Hitman

## Fluents :
	Hitman (x, y), vide (x, y), orientation_hitman(x, y), possede_arme, possede_costume, target_is_down


## Etat initial :
	Hitman (0, 0), target (0, 3), costume (3, 5), arme (5, 0), garde (4, 5), garde (3, 2), invité (5, 2),
	invité (5, 3), invité (6, 2), mur (2, 0), mur (3, 0), mur (0, 2), mur (1, 2), mur (1, 3), mur (1, 4),
	mur (5, 5), mur (6, 5), voisin (0, 0, 1, 0), voisin (0, 0, 0, 1), voisin (1, 0, 1, 1), voisin (1, 0, 0, 0),
	voisin (0, 1, 1, 1), voisin (0, 1, 0, 0), voisin (1, 1, 0, 1), voisin (1, 1, 1, 0), voisin (1, 1, 2, 1),
	voisin(2, 1, 3, 1), voisin (2, 1, 2, 2), voisin (2, 1, 1, 1), voisin (2, 2, 2, 3), voisin (2, 2, 2, 1),
	voisin(2, 2, 3, 2), voisin(2, 3, 2, 2), voisin(2, 3, 3, 3), voisin(2, 4, 3, 4), voisin(2, 4, 2, 5),
	voisin(2, 4, 2, 3), voisin(2, 5, 2, 4), voisin(2, 5, 2, 6), voisin(2, 5, 1, 5), voisin(1, 5, 2, 4), 	
	voisin(1, 5, 0, 5), voisin(0, 5, 0, 4), voisin(0, 5, 1, 5), voisin(0, 4, 0, 3), voisin(0, 4, 0, 5),  
	voisin(3, 5, 2, 5), voisin(3, 5, 2, 4), voisin(3, 5, 3, 4), voisin(3, 4, 3, 5), voisin(3, 4, 4, 4),
	voisin(3, 4, 3, 3), voisin(3, 4, 2, 4), voisin(3, 3, 3, 4), voisin(3, 3, 4, 3), voisin(3, 3, 3, 2),
	voisin(3, 3, 2, 3), voisin(3, 2, 3, 3), voisin(3, 2, 4, 3), voisin(3, 2, 3, 1), voisin(3, 2, 2, 2),
	voisin(3, 1, 3, 2), voisin(3, 1, 4, 1), voisin(3, 1, 3, 0), voisin(3, 1, 2, 1), voisin(3, 0, 3, 1),
	voisin(3, 0, 4, 0), voisin(3, 0, 2, 0), voisin(4, 5, 4, 4), voisin(4, 5, 3, 5), voisin(4, 4, 4, 5),
	voisin(4, 4, 5, 4), voisin(4, 4, 4, 3), voisin(4, 4, 3, 4), voisin(4, 3, 4, 4), voisin(4, 3, 5, 3),
	voisin(4, 3, 4, 2), voisin(4, 3, 3, 3), voisin(4, 2, 4, 3), voisin(4, 2, 5, 2), voisin(4, 2, 4, 1),
	voisin(4, 2, 3, 2), voisin(4, 1, 4, 2), voisin(4, 1, 5, 1), voisin(4, 1, 4, 0), voisin(4, 1, 3, 1),
	voisin(4, 0, 4, 1), voisin(4, 0, 5, 0), voisin(5, 4, 5, 3), voisin(5, 4, 6, 4), voisin(5, 4, 4, 4),
	voisin(5, 3, 5, 4), voisin(5, 3, 6, 3), voisin(5, 3, 5, 2), voisin(5, 3, 4, 3), voisin(5, 2, 5, 3),
	voisin(5, 2, 6, 2), voisin(5, 2, 5, 1), voisin(5, 2, 4, 2), voisin(5, 1, 5, 2), voisin(5, 1, 6, 1),
	voisin(5, 1, 5, 0), voisin(5, 1, 4, 1), voisin(5, 0, 5, 1), voisin(5, 0, 6, 0), voisin(5, 0, 4, 0),
	voisin(6, 4, 6, 3), voisin(6, 4, 5, 4), voisin(6, 3, 6, 2), voisin(6, 3, 5, 3), voisin(6, 3, 6, 4),
	voisin(6, 2, 6, 3), voisin(6, 2, 6, 1), voisin(6, 2, 5, 2), voisin(6, 1, 6, 2), voisin(6, 1, 6, 0),
	voisin(6, 1, 5, 1), voisin(6, 0, 6, 1), voisin(6, 0, 5, 0), orientation_hitman(1, 0), 
	orientation_gardes(4, 5, 4, 4), orientation_gardes(3, 2, 4, 2), orientation_invités(5, 2, 6, 2),
	orientation_invités(5, 3, 5, 4), orientation_invités(6, 2, 5, 2),

## But :
	Goal (Hitman (0, 0) ET target_is_down) 

## Actions :
	Avancer (x, y, x', y')
		PRECOND : Hitman (x, y) ET Vide (x', y') ET Voisin (x, y, x', y')
		EFFECT : Vide (x, y) ET Hitman (x', y')
	neutraliser_garde (x, y, x’, y’)
		PRECOND : garde (x, y) ET hitman (x', y') ET orientation_hitman(x, y) ET NON orientation_gardes(x, y, x', y') ET Voisin (x, y, x', y')
		EFFECT : Vide (x, y) ET NON garde (x, y)
	tuer_cible (x, y)
		PRECOND : target (x, y) ET hitman (x, y) ET possede_arme
		EFFECT : target_is_down
	neutraliser_civil (x, y)
		PRECOND : civil (x, y) ET hitman (x', y') ET orientation_hitman(x, y) ET NON orientation_inivités(x, y, x', y') ET Voisin (x, y, x', y')
		EFFECT : Vide (x, y) ET NON civil (x, y)
	prendre_arme (x, y)	
		PRECOND : arme (x, y) ET hitman (x, y)
		EFFECT : possede_arme ET NON arme (x, y)
	prendre_costume (x, y)
		PRECOND : costume (x, y) ET hitman (x, y)
		EFFECT : possede_costume ET NON costume (x, y)
