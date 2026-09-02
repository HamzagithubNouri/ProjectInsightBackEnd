Issue Type: Repeated Database Queries
Category: Performance
Severity: Medium

Description:
La meme requete (identique ou quasi identique) est executee plusieurs fois dans
la meme fonction ou le meme flux de traitement, alors que le resultat pourrait
etre recupere une seule fois et reutilise.

Why is it a problem:
Chaque requete a un cout reseau et de traitement cote base de donnees — repeter
inutilement une requete identique gaspille des ressources et ralentit la reponse
sans aucun benefice, puisque le resultat n'a pas change entre les appels.

Bad Example:
def get_team_summary(team_id, db):
    name = db.query(Team).filter(Team.id == team_id).first().name
    members_count = len(db.query(Team).filter(Team.id == team_id).first().members)
    leader = db.query(Team).filter(Team.id == team_id).first().leader_id
    return {"name": name, "members": members_count, "leader": leader}

Good Example:
def get_team_summary(team_id, db):
    team = db.query(Team).filter(Team.id == team_id).first()
    return {"name": team.name, "members": len(team.members), "leader": team.leader_id}

How to Fix:
Recuperer une seule fois le resultat d'une requete dans une variable, puis
reutiliser cette variable pour tous les usages ulterieurs dans la meme fonction,
au lieu de refaire la requete a chaque acces.

Common Student Mistakes:
- Ecrire chaque acces a une donnee comme une requete independante sans se rendre compte de la repetition
- Ne pas remarquer le probleme car chaque requete individuelle est rapide, seul le cumul pose probleme

Educational Explanation:
Ce probleme est une forme specifique de duplication de code, mais avec un cout
de performance direct en plus du cout de lisibilite : chaque requete repetee
ajoute une latence reseau meme si la base de donnees repond vite, ce cout
s'additionne a chaque appel identique evitable.

Related Concepts: Query Caching, Code Duplication, Database Round-trips, Memoization