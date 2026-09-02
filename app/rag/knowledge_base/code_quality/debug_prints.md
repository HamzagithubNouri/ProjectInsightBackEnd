Issue Type: Debug Prints Left in Code
Category: Code Quality
Severity: Low

Description:
Des instructions print() ou console.log() utilisees pour deboguer pendant le
developpement sont oubliees et restent dans le code envoye en production.

Why is it a problem:
Ca pollue les logs reels avec des informations non structurees et non filtrables,
peut exposer accidentellement des donnees sensibles dans les logs, et n'offre
aucun controle sur le niveau de verbosite (contrairement a un vrai systeme de
logging).

Bad Example:
def process_payment(user, amount):
    print(f"DEBUG: user={user}, amount={amount}")
    result = charge_card(user, amount)
    print(result)
    return result

Good Example:
import logging
log = logging.getLogger(__name__)

def process_payment(user, amount):
    log.debug("Traitement paiement", extra={"user_id": user.id, "amount": amount})
    result = charge_card(user, amount)
    log.info("Paiement traite", extra={"status": result.status})
    return result

How to Fix:
Remplacer les print() de debogage par un vrai systeme de logging (module
logging en Python), qui permet de filtrer par niveau (debug/info/warning/error)
et de rediriger vers des fichiers ou services de monitoring en production.

Common Student Mistakes:
- Utiliser print() pour deboguer un probleme, puis oublier de le retirer une fois corrige
- Ne pas connaitre le module logging et considerer print() comme suffisant pour tout usage

Educational Explanation:
Un systeme de logging structure permet de decider APRES coup (en production, sans
redeployer) quel niveau de detail afficher, alors que print() est tout ou rien
et grave definitivement dans le code. Le logging permet aussi d'ajouter du
contexte structure (user_id, timestamp, module) exploitable par des outils
d'analyse de logs.

Related Concepts: Logging Levels, Observability, Structured Logging, Production Readiness