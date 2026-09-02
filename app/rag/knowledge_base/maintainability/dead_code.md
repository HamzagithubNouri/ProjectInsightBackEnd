Issue Type: Dead Code
Category: Maintainability
Severity: Low

Description:
Du code qui n'est jamais execute (fonctions non appelees, branches conditionnelles
inatteignables, code commente laisse dans le fichier) mais qui reste present dans
le code source.

Why is it a problem:
Le code mort induit en erreur les futurs lecteurs qui peuvent penser qu'il est
utilise, ralentit la comprehension globale du fichier, et augmente le risque
qu'un developpeur le modifie en pensant a tort qu'il a un effet.

Bad Example:
def calculate_price(item):
    # ancienne version, ne plus utiliser
    # return item.base_price * 1.2
    return item.base_price * item.tax_rate

def old_unused_function():
    pass  # jamais appelee nulle part dans le projet

Good Example:
def calculate_price(item):
    return item.base_price * item.tax_rate
# ancienne version et fonction inutilisee supprimees ;
# l'historique reste consultable via git log/git blame si besoin

How to Fix:
Supprimer le code commente et les fonctions/variables inutilisees plutot que de
les laisser "au cas ou" — l'historique Git conserve deja toutes les versions
precedentes si besoin de les retrouver un jour.

Common Student Mistakes:
- Commenter du code au lieu de le supprimer par peur d'en avoir besoin plus tard
- Laisser des fonctions de test/debug temporaires dans le code final

Educational Explanation:
Git existe precisement pour resoudre le probleme que le code commente essaie de
resoudre manuellement : conserver l'historique des versions precedentes. Le code
source actuel devrait toujours representer uniquement ce qui est reellement en
usage — tout le reste alourdit la lecture sans apporter de valeur.

Related Concepts: Version Control, YAGNI Principle, Code Cleanliness, Refactoring