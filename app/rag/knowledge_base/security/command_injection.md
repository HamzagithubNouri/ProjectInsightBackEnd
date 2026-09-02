Issue Type: Command Injection
Category: Security
Severity: Critical

Description:
Survient quand une application execute une commande systeme construite a partir
d'une entree utilisateur non validee, permettant a un attaquant d'injecter des
commandes shell arbitraires.

Why is it a problem:
Un attaquant peut executer n'importe quelle commande sur le serveur (lister des
fichiers, lire des donnees sensibles, installer un malware, effacer des donnees)
avec les privileges du processus de l'application.

Bad Example:
import os
filename = request.args.get("file")
os.system(f"cat {filename}")
# filename = "a.txt; rm -rf /" execute deux commandes

Good Example:
import subprocess
filename = request.args.get("file")
subprocess.run(["cat", filename], shell=False)
# les arguments sont passes comme liste, jamais interpretes par un shell

How to Fix:
Ne jamais construire de commande shell par concatenation de chaines. Utiliser des
fonctions qui prennent les arguments sous forme de liste (shell=False), et valider
strictement les entrees (whitelist de caracteres autorises) si un shell est
absolument necessaire.

Common Student Mistakes:
- Utiliser os.system() ou shell=True par habitude sans y penser
- Valider seulement l'extension du fichier, pas son contenu ni les caracteres speciaux
- Penser qu'un environnement local/de developpement rend le risque acceptable

Educational Explanation:
Un shell interprete des caracteres comme ;, &&, |, ` comme des separateurs ou
executeurs de commandes. Des qu'une entree utilisateur passe par un shell, ces
caracteres redonnent le controle a l'attaquant sur ce qui est execute, meme si
l'intention du developpeur etait d'executer une seule commande simple.

Related Concepts: Shell Escaping, Input Validation, Principle of Least Privilege, Sandboxing