Issue Type: Inconsistent Style
Category: Code Quality
Severity: Low

Description:
Le code melange plusieurs conventions de nommage ou de formatage dans le meme
projet (camelCase et snake_case, indentation variable, guillemets simples et
doubles sans regle claire).

Why is it a problem:
Un style incoherent augmente la charge cognitive de lecture (le cerveau doit
constamment s'ajuster a des conventions differentes) et rend les diffs Git plus
bruyants quand quelqu'un "corrige" accidentellement le style en modifiant une
fonctionnalite.

Bad Example:
def getUserData(user_id):
    userName = fetch_name(user_id)
    user_email = fetch_email(user_id)
    return {"name":userName,'email': user_email}

Good Example:
def get_user_data(user_id):
    user_name = fetch_name(user_id)
    user_email = fetch_email(user_id)
    return {"name": user_name, "email": user_email}

How to Fix:
Adopter un style guide standard pour le langage (PEP8 pour Python) et utiliser
un formateur automatique (Black, autopep8) plutot que de compter sur la
discipline manuelle de chaque contributeur.

Common Student Mistakes:
- Melanger le style d'un langage habituel (JavaScript camelCase) avec Python (snake_case) par habitude
- Ne pas configurer de formateur automatique dans le projet, laissant chaque membre de l'equipe formater a sa maniere

Educational Explanation:
La coherence de style compte plus que le choix precis du style lui-meme — ce
qui importe est qu'un seul standard soit applique partout dans le projet, pour
que le lecteur puisse se concentrer sur la logique plutot que sur les variations
de forme. Un outil de formatage automatique (execute en pre-commit ou en CI)
elimine ce probleme sans effort humain repete.

Related Concepts: Style Guides, PEP8, Automated Formatting (Black), Code Consistency