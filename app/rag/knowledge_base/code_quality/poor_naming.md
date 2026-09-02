Issue Type: Poor Naming
Category: Code Quality
Severity: Medium

Description:
Des noms de variables, fonctions ou classes non descriptifs (x, tmp, data, foo,
liste2) qui ne communiquent pas leur intention ou leur contenu.

Why is it a problem:
Le lecteur doit lire tout le corps de la fonction pour comprendre ce qu'une
variable represente vraiment, au lieu de le deduire immediatement du nom — le
code prend plus de temps a comprendre et a maintenir correctement.

Bad Example:
def calc(x, y, z):
    a = x * y
    if z:
        a = a * 0.9
    return a

Good Example:
def calculate_total_price(unit_price, quantity, has_discount):
    total = unit_price * quantity
    if has_discount:
        total = total * 0.9
    return total

How to Fix:
Choisir des noms qui decrivent le role ou le contenu de la variable/fonction,
meme si c'est plus long a ecrire — le temps gagne a la lecture (bien plus
frequente que l'ecriture) compense largement.

Common Student Mistakes:
- Utiliser des noms courts pour "aller plus vite" en ecrivant le code
- Nommer une variable d'apres son type plutot que son role (liste_1 au lieu de active_users)

Educational Explanation:
Le code est lu bien plus souvent qu'il n'est ecrit — par toi-meme dans six mois,
par un camarade de projet, par ton enseignant en revue. Un bon nom de variable
elimine le besoin d'un commentaire pour expliquer ce qu'elle contient : le nom
EST la documentation.

Related Concepts: Self-Documenting Code, Code Readability, Naming Conventions, PEP8