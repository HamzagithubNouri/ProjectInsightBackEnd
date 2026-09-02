Issue Type: Hardcoded Secrets
Category: Security
Severity: Critical

Description:
Des identifiants sensibles (mots de passe, cles API, tokens, cles de chiffrement)
sont ecrits directement en dur dans le code source plutot que geres via un
mecanisme de configuration securise.

Why is it a problem:
Le secret se retrouve dans l'historique Git (meme apres suppression du fichier),
visible par toute personne ayant acces au depot, et souvent copie-colle dans des
environnements de developpement, de test, voire publie par erreur sur un depot public.

Bad Example:
DATABASE_PASSWORD = "SuperSecret123!"
API_KEY = "sk-abc123xyz789"

Good Example:
import os
DATABASE_PASSWORD = os.environ["DATABASE_PASSWORD"]
API_KEY = os.environ["API_KEY"]
# valeurs fournies via un fichier .env non commite (voir .gitignore)

How to Fix:
Stocker tous les secrets dans des variables d'environnement ou un gestionnaire de
secrets dedie (Vault, AWS Secrets Manager), jamais dans le code source. Ajouter
les fichiers .env au .gitignore des le debut du projet.

Common Student Mistakes:
- Commiter un fichier .env par erreur car il n'etait pas dans le .gitignore initial
- Mettre un secret "juste pour tester", puis oublier de le retirer avant le commit
- Croire qu'un depot prive suffit a proteger un secret expose dans le code

Educational Explanation:
Un secret commite dans Git reste dans l'historique meme apres avoir ete supprime
dans un commit ulterieur — il faut reecrire l'historique entier (et considerer le
secret comme compromis) pour vraiment le retirer. La bonne pratique est donc de
ne jamais l'ecrire en dur des le depart, plutot que de compter sur une suppression
ulterieure.

Related Concepts: Environment Variables, Secrets Management, .gitignore, Least Privilege