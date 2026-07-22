from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.schemas.repository_schema import RepositoryConnect
from app.schemas.team_schema import MyTeamOut, TeamMemberInfo
from app.repositories import team_repository, github_repo_repository


def connect_repository(db: Session, team_id: int, data: RepositoryConnect, current_user):
    """Seul le TEAM LEADER peut connecter/modifier le repository de l'equipe."""
    team = team_repository.get_team_by_id(db, team_id)
    if team is None:
        raise HTTPException(status_code=404, detail="Equipe introuvable")

    if team.leader_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seul le Team Leader peut connecter ou modifier le repository",
        )

    return github_repo_repository.connect_repository(db, team_id, data, current_user.id)


def get_repository(db: Session, team_id: int, current_user):
    """Lecture seule : accessible a tout membre de l'equipe (leader ou non)."""
    if not team_repository.is_student_in_team(db, team_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'etes pas membre de cette equipe",
        )

    repo = github_repo_repository.get_repository_by_team(db, team_id)
    if repo is None:
        raise HTTPException(status_code=404, detail="Aucun repository connecte pour cette equipe")
    return repo


def get_my_team(db: Session, current_user) -> MyTeamOut:
    """Renvoie toutes les infos de la page 'My Team' : equipe, classe, leader,
    membres, repository, et le role de l'utilisateur courant dans CETTE equipe."""
    team = team_repository.get_team_by_student(db, current_user.id)
    if team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vous n'etes assigne a aucune equipe pour le moment",
        )

    member_rows = team_repository.get_team_members(db, team.id)
    members = [
        TeamMemberInfo(
            id=row.student.id,
            first_name=row.student.first_name,
            last_name=row.student.last_name,
            email=row.student.email,
            is_leader=(row.student.id == team.leader_id),
        )
        for row in member_rows
    ]
    leader = next((m for m in members if m.is_leader), None)

    repo = github_repo_repository.get_repository_by_team(db, team.id)
    my_role = "LEADER" if team.leader_id == current_user.id else "MEMBER"

    return MyTeamOut(
        team_id=team.id,
        team_name=team.name,
        class_name=team.school_class.name,
        leader=leader,
        members=members,
        repository=repo,
        my_team_role=my_role,
    )
