Issue Type: Unused Imports
Category: Code Quality
Severity: Low

Description:
Un module ou une fonction est importe en debut de fichier mais n'est jamais
utilise dans le reste du code.

Why is it a problem:
Ca induit en erreur sur les dependances reelles du fichier, peut ralentir
legerement le temps de chargement, et signale souvent un refactoring incomplet
(le code qui utilisait cet import a ete supprime, mais pas l'import lui-meme).

Bad Example:
import json
import logging
from typing import List

def get_users() -> List[str]:
    return ["alice", "bob"]
# json et logging ne sont jamais utilises

Good Example:
from typing import List

def get_users() -> List[str]:
    return ["alice", "bob"]

How to Fix:
Supprimer les imports non utilises. La plupart des IDE (VS Code, PyCharm) les
signalent visuellement, et un linter comme Pyflakes les detecte automatiquement
en CI.

Common Student Mistakes:
- Copier le bloc d'imports d'un autre fichier "au cas ou" sans verifier ce qui est reellement necessaire
- Oublier de nettoyer les imports apres avoir supprime du code qui les utilisait

Educational Explanation:
Les imports d'un fichier devraient refleter exactement ses dependances reelles —
un lecteur (ou un outil d'analyse de dependances) doit pouvoir se fier a la liste
des imports pour savoir de quoi le module a besoin, sans avoir a verifier
manuellement si chaque import est reellement utilise.

Related Concepts: Linting, Dependency Management, Static Analysis, Import Hygiene