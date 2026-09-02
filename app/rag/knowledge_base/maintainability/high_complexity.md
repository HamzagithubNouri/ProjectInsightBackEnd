Issue Type: High Cyclomatic Complexity
Category: Maintainability
Severity: Medium

Description:
Une fonction contient trop de chemins d'execution distincts (conditions, boucles,
branches imbriquees), rendant difficile de raisonner sur tous les cas possibles.

Why is it a problem:
Plus il y a de chemins possibles, plus il est facile qu'un cas limite soit oublie
lors des tests ou d'une modification future, et plus il est difficile pour un
autre developpeur de comprendre rapidement ce que fait la fonction.

Bad Example:
def get_discount(user, order, promo):
    if user.is_premium:
        if order.total > 100:
            if promo and promo.valid:
                return 0.3
            else:
                return 0.2
        else:
            if promo and promo.valid:
                return 0.15
            else:
                return 0.1
    else:
        if promo and promo.valid:
            return 0.05
        return 0

Good Example:
def get_discount(user, order, promo):
    base = 0.2 if user.is_premium and order.total > 100 else 0.1 if user.is_premium else 0
    promo_bonus = 0.1 if promo and promo.valid else 0
    return base + promo_bonus

How to Fix:
Extraire les sous-conditions en fonctions nommees explicitement, remplacer les
conditions imbriquees par des combinaisons booleennes ou une table de decision,
et privilegier les retours anticipes (early return) pour reduire l'imbrication.

Common Student Mistakes:
- Ajouter des "if" supplementaires au fur et a mesure des besoins, sans jamais restructurer
- Ne pas utiliser d'outil de mesure (comme Radon) pour prendre conscience de la complexite reelle

Educational Explanation:
La complexite cyclomatique compte le nombre de chemins independants dans une
fonction — c'est aussi, approximativement, le nombre minimum de tests unitaires
necessaires pour couvrir tous les cas. Une fonction avec une complexite de 15
necessite donc potentiellement 15 tests differents pour etre bien couverte,
ce qui est un signal clair qu'elle devrait etre decoupee.

Related Concepts: Cyclomatic Complexity, Early Return, Decision Tables, Guard Clauses