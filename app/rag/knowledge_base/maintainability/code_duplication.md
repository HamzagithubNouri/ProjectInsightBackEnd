Issue Type: Code Duplication
Category: Maintainability
Severity: Medium

Description:
Le meme bloc de logique (ou tres similaire) est repete a plusieurs endroits du
code au lieu d'etre factorise dans une fonction ou une classe partagee.

Why is it a problem:
Un bug corrige a un endroit doit etre corrige manuellement partout ou le code est
duplique — un endroit oublie reintroduit le meme bug. Ca augmente aussi la taille
du code sans ajouter de valeur.

Bad Example:
def send_welcome_email(user):
    if not user.email or "@" not in user.email:
        raise ValueError("email invalide")
    ...
def send_reset_email(user):
    if not user.email or "@" not in user.email:
        raise ValueError("email invalide")
    ...

Good Example:
def validate_email(email):
    if not email or "@" not in email:
        raise ValueError("email invalide")

def send_welcome_email(user):
    validate_email(user.email)
    ...
def send_reset_email(user):
    validate_email(user.email)
    ...

How to Fix:
Des qu'un bloc de logique apparait deux fois de facon quasi identique, l'extraire
dans une fonction partagee et appeler cette fonction aux deux endroits.

Common Student Mistakes:
- Copier-coller une fonction existante pour aller vite, en modifiant juste un detail
- Dupliquer plutot que de prendre le temps de comprendre le code existant pour le reutiliser

Educational Explanation:
La regle informelle "rule of three" : une duplication ponctuelle (2 occurrences)
peut parfois etre acceptable si les deux evolueront differemment, mais des la
3e occurrence quasi identique, il faut factoriser — c'est un signal fort que
cette logique est une regle metier reelle, pas une coincidence.

Related Concepts: DRY Principle, Refactoring, Rule of Three, Abstraction