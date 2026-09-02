Issue Type: Unnecessary Loops
Category: Performance
Severity: Medium

Description:
Une boucle manuelle est utilisee pour une operation que le langage ou une
bibliotheque fournit deja de facon optimisee (recherche, filtrage, transformation,
agregation).

Why is it a problem:
Les implementations natives (built-ins, fonctions de bibliotheque) sont
generalement ecrites dans un langage compile plus rapide et optimisees, alors
qu'une boucle Python manuelle s'execute ligne par ligne dans l'interpreteur —
souvent plusieurs fois plus lente sur de gros volumes de donnees.

Bad Example:
total = 0
for num in numbers:
    total = total + num

found = False
for item in items:
    if item.id == target_id:
        found = True
        break

Good Example:
total = sum(numbers)

found = any(item.id == target_id for item in items)

How to Fix:
Utiliser les fonctions built-in adaptees (sum, max, min, any, all, sorted) et les
comprehensions de liste plutot que d'ecrire manuellement une boucle equivalente,
sauf si la logique est trop specifique pour s'y preter.

Common Student Mistakes:
- Ne pas connaitre les fonctions built-in disponibles (sum, any, all) et les reimplementer
- Utiliser une boucle for avec un flag manuel au lieu de any()/all() ou d'un break bien place

Educational Explanation:
Au-dela de la performance, utiliser sum(numbers) plutot qu'une boucle manuelle
communique immediatement l'intention au lecteur ("je fais une somme") sans qu'il
ait besoin d'analyser la boucle pour deviner ce qu'elle calcule — c'est a la fois
plus rapide et plus lisible.

Related Concepts: Built-in Functions, List Comprehensions, Vectorization, Big O Complexity