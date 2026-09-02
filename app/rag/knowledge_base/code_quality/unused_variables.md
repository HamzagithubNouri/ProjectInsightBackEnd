Issue Type: Unused Variables
Category: Code Quality
Severity: Low

Description:
Une variable est declaree et assignee mais jamais lue ni utilisee ensuite dans
le code.

Why is it a problem:
C'est souvent le signe d'un bug (une valeur qui devait etre utilisee a ete
oubliee), et ca alourdit inutilement la lecture du code pour ceux qui essaient
de comprendre ce qui est reellement necessaire.

Bad Example:
def calculate_total(items):
    tax_rate = 0.2  # jamais utilise
    total = sum(item.price for item in items)
    return total

Good Example:
def calculate_total(items):
    tax_rate = 0.2
    total = sum(item.price for item in items) * (1 + tax_rate)
    return total

How to Fix:
Soit supprimer la variable si elle n'a effectivement aucune utilite, soit
l'utiliser reellement si son absence revele un oubli dans la logique.

Common Student Mistakes:
- Laisser une variable de debug ou d'un ancien brouillon de logique
- Assigner une valeur "au cas ou" sans jamais s'en servir

Educational Explanation:
Une variable inutilisee force le lecteur a se demander "est-ce que j'ai manque
quelque chose, ou est-ce vraiment inutile ?" — cette ambiguite a un cout de
lecture reel. Un linter (Pylint, Pyflakes) detecte automatiquement ces cas, ce
qui en fait un des controles de qualite les plus simples a automatiser.

Related Concepts: Linting, Static Analysis, Code Readability, Dead Code