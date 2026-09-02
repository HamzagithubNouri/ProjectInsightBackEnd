Issue Type: Insecure Deserialization
Category: Security
Severity: Critical

Description:
Survient quand une application deserialise des donnees provenant d'une source
non fiable (utilisateur, reseau) sans validation, en particulier avec des formats
capables d'executer du code lors de la deserialisation (pickle en Python).

Why is it a problem:
Certains formats de serialisation (pickle notamment) peuvent executer du code
arbitraire pendant la deserialisation elle-meme. Un attaquant qui controle les
donnees serialisees peut donc executer n'importe quel code sur le serveur.

Bad Example:
import pickle
data = pickle.loads(request.body)  # execute potentiellement du code arbitraire

Good Example:
import json
data = json.loads(request.body)  # JSON ne peut pas executer de code

How to Fix:
Ne jamais utiliser pickle (ou des formats equivalents comme yaml.load non securise)
sur des donnees provenant de l'exterieur. Utiliser JSON ou un format de donnees
pur sans capacite d'execution de code pour tout echange avec une source non fiable.

Common Student Mistakes:
- Utiliser pickle pour la "simplicite" de sauvegarder/charger des objets Python complexes
- Utiliser yaml.load() au lieu de yaml.safe_load()
- Ne pas realiser que le probleme existe des la deserialisation, avant meme d'utiliser la donnee

Educational Explanation:
La difference cle entre JSON et pickle : JSON decrit uniquement des donnees
(nombres, chaines, listes, objets), alors que pickle serialise des objets Python
entiers, y compris des instructions d'execution pour reconstruire ces objets.
Deserialiser un pickle revient litteralement a executer du code fourni par la
source des donnees.

Related Concepts: Serialization Formats, Remote Code Execution, Input Validation, Sandboxing