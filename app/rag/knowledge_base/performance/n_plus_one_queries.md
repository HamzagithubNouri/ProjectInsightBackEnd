Issue Type: N+1 Queries
Category: Performance
Severity: High

Description:
Une requete initiale recupere N enregistrements, puis une requete supplementaire
distincte est executee pour CHAQUE enregistrement afin de recuperer des donnees
liees, resultant en N+1 requetes au lieu d'une seule requete optimisee.

Why is it a problem:
Avec 100 enregistrements, ca signifie 101 allers-retours vers la base de donnees
au lieu d'un ou deux — chaque aller-retour a une latence reseau fixe, donc le
temps total explose lineairement avec le nombre d'enregistrements.

Bad Example:
teams = db.query(Team).all()
for team in teams:
    members = db.query(TeamMember).filter(TeamMember.team_id == team.id).all()
    # une requete SQL par equipe : N+1 requetes au total

Good Example:
from sqlalchemy.orm import joinedload
teams = db.query(Team).options(joinedload(Team.members)).all()
# une seule requete SQL avec JOIN, les membres sont deja charges

How to Fix:
Utiliser le eager loading de l'ORM (joinedload, selectinload en SQLAlchemy) pour
charger les relations en une seule requete plutot qu'une requete par ligne
parcourue dans une boucle.

Common Student Mistakes:
- Ne pas remarquer le probleme en developpement local avec peu de donnees (5 equipes = 6 requetes, invisible)
- Faire une requete dans une boucle for par habitude, sans penser au cout cumule

Educational Explanation:
Ce probleme est souvent invisible en developpement (peu de donnees de test) mais
devient critique en production avec de vrais volumes de donnees — c'est pour ca
qu'il faut le connaitre et l'eviter par principe des l'ecriture du code, plutot
que de compter sur le fait de le remarquer plus tard via des tests de charge.

Related Concepts: Eager Loading, ORM Query Optimization, Database Round-trips, joinedload