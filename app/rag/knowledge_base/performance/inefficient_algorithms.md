Issue Type: Inefficient Algorithms
Category: Performance
Severity: Medium

Description:
Un algorithme avec une complexite temporelle superieure a necessaire est utilise
pour resoudre un probleme (par exemple une recherche lineaire repetee dans une
liste alors qu'un dictionnaire ou un set offrirait un acces direct).

Why is it a problem:
Sur de petits volumes de donnees, la difference est invisible, mais elle devient
critique a mesure que les donnees grandissent — un algorithme en O(n^2) devient
rapidement injouable sur des milliers d'elements, alors qu'un equivalent en
O(n log n) ou O(n) reste rapide.

Bad Example:
def find_duplicates(items):
    duplicates = []
    for i, item in enumerate(items):
        for other in items[i+1:]:
            if item == other:
                duplicates.append(item)
    return duplicates
# O(n^2) : compare chaque element a tous les autres

Good Example:
def find_duplicates(items):
    seen = set()
    duplicates = set()
    for item in items:
        if item in seen:
            duplicates.add(item)
        seen.add(item)
    return list(duplicates)
# O(n) : un seul passage, recherche en O(1) grace au set

How to Fix:
Utiliser des structures de donnees adaptees a l'operation dominante : un set ou
dict pour des recherches/verifications d'appartenance frequentes (O(1) en
moyenne) plutot qu'une liste (O(n) par recherche).

Common Student Mistakes:
- Utiliser "in" sur une liste dans une boucle sans realiser que chaque verification est O(n)
- Ne pas connaitre la difference de complexite entre list, set et dict pour les recherches

Educational Explanation:
La notation Big O decrit comment le temps d'execution grandit avec la taille des
donnees, pas le temps absolu pour une taille donnee. Un algorithme O(n^2) peut
sembler tout aussi rapide qu'un O(n) sur 10 elements, mais sur 100 000 elements
la difference devient une question de millisecondes contre plusieurs minutes.

Related Concepts: Big O Notation, Hash Tables, Time Complexity, Data Structure Selection