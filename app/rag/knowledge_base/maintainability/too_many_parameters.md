Issue Type: Too Many Parameters
Category: Maintainability
Severity: Low

Description:
Une fonction accepte un nombre eleve de parametres (generalement plus de 4-5),
rendant les appels difficiles a lire et sujets a des erreurs d'ordre des arguments.

Why is it a problem:
Il devient facile d'inverser accidentellement deux parametres de meme type
(par exemple deux booleens ou deux chaines) sans que Python ou le lecteur ne le
remarque, et chaque appel de la fonction devient difficile a comprendre sans
consulter sa signature.

Bad Example:
def create_user(first_name, last_name, email, password, role, class_id, is_active, send_email):
    ...

create_user("Jean", "Dupont", "j@x.com", "pwd123", "student", 3, True, False)

Good Example:
from dataclasses import dataclass

@dataclass
class UserCreationRequest:
    first_name: str
    last_name: str
    email: str
    password: str
    role: str
    class_id: int
    is_active: bool = True
    send_email: bool = False

def create_user(request: UserCreationRequest):
    ...

How to Fix:
Regrouper les parametres lies dans un objet dedie (dataclass, Pydantic model),
ou utiliser des arguments nommes obligatoires (keyword-only) pour au moins
rendre les appels explicites et moins ambigus.

Common Student Mistakes:
- Ajouter un parametre supplementaire a chaque nouveau besoin plutot que de restructurer
- Appeler la fonction avec des arguments positionnels au lieu de nommes, rendant l'ordre critique et invisible

Educational Explanation:
Un nombre eleve de parametres est souvent un signal que la fonction fait trop
de choses, ou que plusieurs de ces parametres representent en realite un seul
concept coherent (par exemple "les informations d'un nouvel utilisateur") qui
merite sa propre structure de donnees plutot que d'etre eclate en variables
independantes.

Related Concepts: Parameter Object Pattern, Data Classes, Keyword-Only Arguments, Cohesion