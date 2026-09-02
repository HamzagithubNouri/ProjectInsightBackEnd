Issue Type: Weak Cryptography
Category: Security
Severity: High

Description:
Utilisation d'algorithmes de hachage ou de chiffrement obsoletes/faibles (MD5,
SHA1 pour des mots de passe, ou absence totale de sel) pour proteger des donnees
sensibles.

Why is it a problem:
MD5 et SHA1 sont rapides a calculer (concus pour l'integrite de fichiers, pas pour
la securite de mots de passe) et peuvent etre casses par force brute ou table
arc-en-ciel en un temps raisonnable, exposant les mots de passe des utilisateurs
en cas de fuite de la base de donnees.

Bad Example:
import hashlib
hashed = hashlib.md5(password.encode()).hexdigest()

Good Example:
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed = pwd_context.hash(password)

How to Fix:
Utiliser un algorithme de hachage concu specifiquement pour les mots de passe
(bcrypt, argon2, scrypt), qui integrent un sel automatique et sont volontairement
lents pour ralentir les attaques par force brute.

Common Student Mistakes:
- Utiliser hashlib.md5() ou hashlib.sha256() directement pour hacher un mot de passe
- Ne pas ajouter de sel, rendant les tables arc-en-ciel efficaces
- Confondre "hachage rapide pour verifier l'integrite d'un fichier" et "hachage pour securiser un mot de passe" — ce sont deux besoins opposes

Educational Explanation:
MD5/SHA1 sont concus pour etre rapides (verifier qu'un fichier telecharge n'est
pas corrompu, par exemple). Pour un mot de passe, la vitesse joue contre toi :
plus le hachage est rapide, plus un attaquant peut tester de combinaisons par
seconde. bcrypt/argon2 sont deliberement lents et ajustables (facteur de cout),
ce qui rend la force brute impraticable meme avec du materiel puissant.

Related Concepts: Salting, Key Derivation Functions, Rainbow Tables, bcrypt/argon2