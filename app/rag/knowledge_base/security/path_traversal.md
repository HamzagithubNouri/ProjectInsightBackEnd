Issue Type: Path Traversal
Category: Security
Severity: High

Description:
Survient quand une application construit un chemin de fichier a partir d'une
entree utilisateur sans le valider, permettant a un attaquant d'acceder a des
fichiers hors du dossier prevu via des sequences comme "../".

Why is it a problem:
Un attaquant peut lire des fichiers systeme sensibles (mots de passe, fichiers
de configuration, code source), voire ecrire des fichiers arbitraires si
l'operation est une ecriture.

Bad Example:
filename = request.args.get("file")
with open(f"/uploads/{filename}") as f:
    return f.read()
# filename = "../../etc/passwd" sort du dossier uploads

Good Example:
import os
filename = os.path.basename(request.args.get("file"))
safe_path = os.path.join("/uploads", filename)
if not os.path.abspath(safe_path).startswith("/uploads"):
    raise ValueError("Chemin invalide")
with open(safe_path) as f:
    return f.read()

How to Fix:
Utiliser os.path.basename() pour ne garder que le nom de fichier (supprime tout
chemin), puis verifier que le chemin final resolu reste bien a l'interieur du
dossier autorise avant d'ouvrir le fichier.

Common Student Mistakes:
- Se contenter de bloquer la sous-chaine ".." sans gerer l'encodage URL (%2e%2e%2f)
- Faire confiance au nom de fichier fourni par le frontend
- Ne pas verifier le chemin absolu final apres resolution

Educational Explanation:
Un chemin de fichier est resolu par le systeme d'exploitation, pas juste lu comme
texte. "../" remonte d'un niveau dans l'arborescence quel que soit le dossier de
depart — la seule protection fiable est de verifier ou le chemin final resolu
pointe reellement, pas de chercher des motifs suspects dans la chaine d'entree.

Related Concepts: Input Sanitization, Chroot Jail, Whitelisting, File System Permissions