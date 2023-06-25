![Python Logo](https://www.python.org/static/community_logos/python-logo-master-v3-TM.png)

# Projet Hitman AI27

Ce projet est le projet final de l'UV AI27.

Membre du groupe:

- Baptiste BUVRON
- Axel PAPILLIER

## Prérequis

Avant de démarrer le script Python, veuillez suivre les étapes ci-dessous :

1. Clonez le projet depuis le référentiel GitHub :

   ```
   git clone https://github.com/BaptisteBuvron/Hitman_AI27
   ```

2. Accédez au répertoire du projet :

   ```
   cd Hitman_AI27
   ```

3. Installez les dépendances requises en exécutant la commande suivante :

   ```
   pip install -r requirements.txt
   ```

## Gophersat

Nous utilisons Gophersat comme solveur SAT, qui est un solveur SAT en ligne de commande écrit en Go.

Pour utiliser le solveur Gophersat, vous devez ajouter le fichier exécutable correspondant à votre système
d'exploitation dans le dossier "/gophersat" du projet. Le nom du fichier exécutable dépend de votre système
d'exploitation :

Pour Windows : gophersat.exe
Pour Linux : gophersat
Pour macOS (architecture AMD) : gophersat_1_13_darwin_amd64
Pour macOS (architecture ARM) : gophersat_1_13_darwin_arm64
Assurez-vous d'avoir téléchargé le fichier exécutable Gophersat correspondant à votre système d'exploitation et de
l'avoir placé dans le dossier "/gophersat" du projet.

## Utilisation du script

Pour exécuter le script principal, veuillez suivre les étapes suivantes :

1. Lancez le fichier `main.py` à l'aide de la commande suivante :

   ```
   python main.py
   ```

   Assurez-vous d'avoir Python installé sur votre système et accessible depuis la ligne de commande.

2. Le script démarrera et exécutera les algorithmes nécessaires pour résoudre le problème du projet Hitman.

Si l'exécution de la phase 1 prend trop de temps, il est possible de désactiver la création des clauses en passant la
variable `debug` à True dans le fichier `main.py`.

## Modélisation SAT

[sat.md](sat.md)

## Modélisation STRIPS

[strips.md](strips.md)

# Retour

Voici les retours sur nos algorithmes, les avantages et les inconvénients

## Phase 1

Pour la phase 1 après avoir fait des tests sur avec différents algorithmes (DFS et dikkstra), nous avons choisi
d'utiliser un algorithme de plus court chemin (dikstra) qui nous permet de venir visiter la case inconnue la plus
proche.
Nous faisons appel à Dijkstra seulement si nous connaissons déjà toutes les cases voisines du hitman.
À chaque itération nous créons les clauses pour le SAT et nous les envoyons au solveur afin d'essayer de déduire le
contenu de certaines cases.

Une possibilité d'amélioration serait de faire appel au solveur pour trouver le plus court chemin entre le hitman et la
case inconnue la plus proche.

## Phase 2

Pour la phase 2, nous avons opté pour un algorithme A* car il était plus efficace pour choisir le chemin optimal tout
en prenant en compte les éléments de la carte et les pénalités. Notre algorithme nous retourne le chemin et nous associons les actions à
chacune des cases à la fin de celui-ci. Nous avons pris la décision de découper notre parcours en 3 appels successifs de
l'algorithme A* (respectivement pour aller chercher l'arme, tuer la cible et revenir).

Une possibilité d'amélioration est que l'heuristique n'est pas parfaitement gérée lorsqu'il tente de tuer des gardes. Le
fait d'ajouter des pénalités importantes à l'heuristique provoque une lenteur de l'algorithme pour de grandes cartes.

La gestion du costume n'est également pas parfaitement gérée étant donné que la résolution de la carte se fait en 3 sous problèmes (aller chercher l'arme, tuer la cible et revenir). 
Il est donc possible que dans certains cas il soit judicieux de prendre le costume même s'il ne fait pas partie du chemin optimal pour un sous problème, mais qu'il permet de résoudre le problème global plus rapidement.