Issue Type: Unnecessary Memory Usage
Category: Performance
Severity: Low

Description:
Le code charge en memoire des donnees entieres (listes, fichiers) alors qu'un
traitement iteratif/en flux (generateurs, lecture ligne par ligne) suffirait,
gaspillant de la memoire inutilement, en particulier sur de gros volumes.

Why is it a problem:
Charger un fichier de plusieurs gigaoctets entierement en memoire avant de le
traiter peut faire planter l'application (memoire insuffisante) alors qu'un
traitement en flux n'aurait besoin que d'une petite quantite de memoire constante
quelle que soit la taille du fichier.

Bad Example:
def count_lines_with_error(filepath):
    with open(filepath) as f:
        lines = f.readlines()  # charge tout le fichier en memoire d'un coup
    return sum(1 for line in lines if "ERROR" in line)

Good Example:
def count_lines_with_error(filepath):
    with open(filepath) as f:
        return sum(1 for line in f if "ERROR" in line)
    # lit et traite le fichier ligne par ligne, memoire constante

How to Fix:
Preferer les generateurs et l'iteration paresseuse (lazy evaluation) aux
structures qui chargent tout en memoire d'un coup, en particulier pour des
fichiers ou des resultats de requetes potentiellement volumineux.

Common Student Mistakes:
- Utiliser .readlines() ou list() par habitude alors qu'une iteration directe suffit
- Charger le resultat complet d'une requete DB (.all()) quand seul un sous-ensemble ou un comptage est necessaire

Educational Explanation:
Un generateur produit les elements un par un, a la demande, sans jamais garder
toute la collection en memoire simultanement — c'est particulierement important
des que la taille des donnees n'est pas connue a l'avance ou peut etre grande
(fichiers logs, exports, resultats de requetes non filtrees).

Related Concepts: Generators, Lazy Evaluation, Streaming, Memory Profiling