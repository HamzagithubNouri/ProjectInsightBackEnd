Issue Type: SQL Injection
Category: Security
Severity: Critical

Description:
Une injection SQL survient quand une entree utilisateur est directement concatenee
dans une requete SQL sans etre echappee ou parametree, permettant a un attaquant
de modifier la structure de la requete elle-meme.

Why is it a problem:
Un attaquant peut lire, modifier ou supprimer des donnees arbitraires dans la base,
contourner l'authentification, ou dans certains cas executer des commandes sur le
serveur de base de donnees.

Bad Example:
query = "SELECT * FROM users WHERE username = '" + username + "'"
cursor.execute(query)

Good Example:
query = "SELECT * FROM users WHERE username = %s"
cursor.execute(query, (username,))

How to Fix:
Toujours utiliser des requetes parametrees (placeholders) fournies par le driver
de base de donnees, jamais de concatenation ou de f-string dans une requete SQL.
Avec un ORM (SQLAlchemy), utiliser les methodes du query builder plutot que du SQL brut.

Common Student Mistakes:
- Utiliser des f-strings pour "simplifier" la requete
- Penser que valider le format cote frontend suffit
- Echapper manuellement les quotes au lieu d'utiliser les parametres du driver

Educational Explanation:
Le probleme n'est pas la presence de donnees utilisateur dans la requete, mais la
maniere dont elles y entrent. Une requete parametree separe strictement la structure
de la requete (fixe, ecrite par le developpeur) des donnees (variables, fournies par
l'utilisateur) — le driver SQL garantit que les donnees ne peuvent jamais etre
interpretees comme du code SQL, quelle que soit leur contenu.

Related Concepts: Parameterized Queries, Input Validation, ORM, Prepared Statements