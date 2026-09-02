Issue Type: Deep Nesting
Category: Maintainability
Severity: Low

Description:
Plusieurs niveaux de conditions ou de boucles imbriquees (souvent 4 niveaux ou
plus), formant un code en forme de "pyramide" difficile a suivre visuellement.

Why is it a problem:
A chaque niveau d'imbrication, le lecteur doit garder en memoire toutes les
conditions des niveaux precedents pour comprendre le code — au-dela de 3-4
niveaux, la charge cognitive devient trop lourde pour suivre facilement.

Bad Example:
def process(items):
    if items:
        for item in items:
            if item.active:
                if item.quantity > 0:
                    if item.price > 0:
                        total += item.price * item.quantity

Good Example:
def process(items):
    if not items:
        return
    for item in items:
        if not (item.active and item.quantity > 0 and item.price > 0):
            continue
        total += item.price * item.quantity

How to Fix:
Utiliser des retours/continue anticipes (guard clauses) pour eliminer les cas
invalides des le debut plutot que d'imbriquer, et combiner les conditions
liees en une seule expression booleenne claire.

Common Student Mistakes:
- Ajouter un nouveau "if" imbrique a chaque nouveau cas a gerer, plutot que de restructurer
- Ne pas connaitre le pattern "guard clause" comme alternative

Educational Explanation:
Un guard clause traite les cas invalides ou limites en premier, avec un retour
immediat, pour que le reste de la fonction puisse supposer que ces cas ont deja
ete elimines. Le code "principal" reste alors au niveau d'imbrication le plus
bas possible, plus facile a lire d'un seul coup d'oeil.

Related Concepts: Guard Clauses, Early Return, Cyclomatic Complexity, Readability