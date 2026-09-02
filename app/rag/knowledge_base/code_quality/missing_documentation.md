Issue Type: Missing Documentation
Category: Code Quality
Severity: Low

Description:
Des fonctions publiques, en particulier celles avec une logique non triviale ou
des parametres ambigus, n'ont pas de docstring expliquant leur but, leurs
parametres et leur valeur de retour.

Why is it a problem:
Un autre developpeur (ou toi-meme plus tard) doit lire et comprendre tout le
corps de la fonction pour savoir comment l'utiliser correctement, au lieu de
lire une description en une ou deux lignes.

Bad Example:
def process(data, threshold):
    return [d for d in data if d["score"] > threshold]

Good Example:
def process(data, threshold):
    """Filtre les elements dont le score depasse le seuil donne.

    Args:
        data: liste de dictionnaires contenant une cle 'score'
        threshold: score minimum (exclusif) pour qu'un element soit garde

    Returns:
        Liste des elements dont le score est strictement superieur a threshold
    """
    return [d for d in data if d["score"] > threshold]

How to Fix:
Ajouter une docstring a chaque fonction publique, decrivant son but, ses
parametres et sa valeur de retour — pas necessaire pour des fonctions privees
triviales (un getter simple, par exemple).

Common Student Mistakes:
- Documenter uniquement le "quoi" evident (repeter le nom de la fonction) plutot que le "pourquoi" ou les cas limites
- Ne documenter que les fonctions complexes en oubliant que le but est justement d'eviter d'avoir a lire le code complexe

Educational Explanation:
Une bonne docstring repond a la question qu'un appelant se pose avant de lire le
code : "que fait cette fonction et comment je l'utilise ?" — c'est un contrat
d'utilisation, pas une redite du code. C'est particulierement important pour
les fonctions dont le comportement n'est pas evident au premier coup d'oeil sur
leur signature.

Related Concepts: Docstrings, Self-Documenting Code, API Contracts, PEP257