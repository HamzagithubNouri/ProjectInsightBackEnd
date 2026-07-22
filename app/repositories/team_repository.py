from sqlalchemy.orm import Session

from app.models.team import Team
from app.models.team_member import TeamMember
from app.models.school_class import SchoolClass


def create_team(db: Session, name: str, class_id: int) -> Team:
    db_team = Team(name=name, class_id=class_id)
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team


def set_leader(db: Session, team_id: int, leader_id: int) -> Team:
    team = db.query(Team).filter(Team.id == team_id).first()
    team.leader_id = leader_id
    db.commit()
    db.refresh(team)
    return team


def add_member(db: Session, team_id: int, student_id: int) -> TeamMember:
    member = TeamMember(team_id=team_id, student_id=student_id)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def add_members_bulk(db: Session, team_id: int, student_ids: list[int]) -> list[TeamMember]:
    members = [TeamMember(team_id=team_id, student_id=sid) for sid in student_ids]
    db.add_all(members)
    db.commit()
    for m in members:
        db.refresh(m)
    return members


def get_team_by_id(db: Session, team_id: int):
    return db.query(Team).filter(Team.id == team_id).first()


def get_team_members(db: Session, team_id: int):
    """Renvoie les lignes TeamMember ; chaque ligne a .student (relation User) deja chargeable."""
    return db.query(TeamMember).filter(TeamMember.team_id == team_id).all()


def is_student_in_team(db: Session, team_id: int, student_id: int) -> bool:
    return (
        db.query(TeamMember)
        .filter(TeamMember.team_id == team_id, TeamMember.student_id == student_id)
        .first()
        is not None
    )


def get_teams_by_teacher(db: Session, teacher_id: int):
    return (
        db.query(Team)
        .join(SchoolClass, Team.class_id == SchoolClass.id)
        .filter(SchoolClass.teacher_id == teacher_id)
        .all()
    )


def get_teams_by_class(db: Session, class_id: int):
    return db.query(Team).filter(Team.class_id == class_id).all()


def get_team_by_student(db: Session, student_id: int):
    """Renvoie la premiere equipe dont cet etudiant est membre.
    LIMITE ACTUELLE : si un etudiant appartient a plusieurs equipes
    (plusieurs semestres/projets), seule la premiere trouvee est renvoyee.
    A affiner plus tard si besoin (ex: parametre semestre/annee actif)."""
    membership = db.query(TeamMember).filter(TeamMember.student_id == student_id).first()
    if membership is None:
        return None
    return membership.team
