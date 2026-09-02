Issue Type: Magic Numbers
Category: Code Quality
Severity: Low

Description:
Des valeurs numeriques (ou parfois des chaines) sont utilisees directement dans
le code sans explication, sans qu'on sache ce qu'elles representent ni pourquoi
cette valeur precise a ete choisie.

Why is it a problem:
Le lecteur ne sait pas si "0.2" represente une TVA, une remise, ou un taux
d'interet, et si cette valeur apparait a plusieurs endroits, la modifier
necessite de la retrouver partout manuellement, avec le risque d'en oublier une.

Bad Example:
def calculate_price(base_price):
    return base_price * 1.2

if user.age > 65:
    apply_senior_discount()

Good Example:
TVA_RATE = 0.2
SENIOR_AGE_THRESHOLD = 65

def calculate_price(base_price):
    return base_price * (1 + TVA_RATE)

if user.age > SENIOR_AGE_THRESHOLD:
    apply_senior_discount()

How to Fix:
Extraire chaque valeur "magique" dans une constante nommee explicitement, placee
en haut du fichier ou dans un module de configuration dedie.

Common Student Mistakes:
- Copier une valeur numerique a plusieurs endroits au lieu de reutiliser une constante
- Nommer la constante d'apres sa valeur plutot que son role (RATE_02 au lieu de TVA_RATE)

Educational Explanation:
Un nombre nomme (TVA_RATE) communique instantanement son intention, alors qu'un
nombre brut (0.2) oblige le lecteur a deviner ou a chercher le contexte. Ca rend
aussi le code plus facile a modifier : changer TVA_RATE = 0.2 en 0.21 met a jour
tous les usages en un seul endroit.

Related Concepts: Named Constants, Configuration Management, Self-Documenting Code, DRY Principle