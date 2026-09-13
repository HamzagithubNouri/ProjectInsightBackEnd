from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.schemas.repository_schema import RepositoryConnect
from app.schemas.team_schema import MyTeamOut, TeamMemberInfo
from app.schemas.ai_review_schema import PRReviewResult
from app.repositories import team_repository, github_repo_repository, user_repository
from app.models.review_history import ReviewHistoryEntry
from app.models.pull_request_review import PullRequestReview
from app.services import github_service, ai_review_service

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
            github_username=row.student.github_username,
            github_linked=row.student.github_username is not None,
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


def get_recent_findings(db: Session, student_id: int, limit: int = 5):
    entries = (
        db.query(ReviewHistoryEntry)
        .filter(ReviewHistoryEntry.student_id == student_id)
        .order_by(ReviewHistoryEntry.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": e.id,
            "filename": e.filename,
            "title": e.finding_title,
            "severity": e.finding_severity,
            "description": e.finding_description,
            "source_type": e.source_type,
            "created_at": e.created_at,
        }
        for e in entries
    ]
    
def _get_repo_and_leader_token(db: Session, team_id: int, current_user):
    """Verifie l'appartenance a l'equipe, recupere le repo connecte et le
    token GitHub du leader (utilise pour TOUS les appels API GitHub, meme
    si c'est un membre simple qui consulte)."""
    if not team_repository.is_student_in_team(db, team_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'etes pas membre de cette equipe")

    team = team_repository.get_team_by_id(db, team_id)
    repo = github_repo_repository.get_repository_by_team(db, team_id)
    if repo is None:
        raise HTTPException(status_code=404, detail="Aucun repository connecte pour cette equipe")

    if team.leader_id is None:
        raise HTTPException(status_code=400, detail="Cette equipe n'a pas de Team Leader assigne")

    leader = user_repository.get_user_by_id(db, team.leader_id)
    if leader is None or not leader.github_access_token:
        raise HTTPException(
            status_code=400,
            detail="Le Team Leader doit connecter son compte GitHub pour voir les Pull Requests",
        )

    owner, repo_name = repo.github_url.rstrip("/").replace("https://github.com/", "").split("/")
    return owner, repo_name, leader.github_access_token


def list_team_pull_requests(db: Session, team_id: int, current_user) -> list[dict]:
    owner, repo_name, token = _get_repo_and_leader_token(db, team_id, current_user)
    prs = github_service.list_pull_requests(token, owner, repo_name)

    reviewed_numbers = {
        row.pr_number for row in
        db.query(PullRequestReview.pr_number).filter(PullRequestReview.team_id == team_id).all()
    }
    for pr in prs:
        pr["already_reviewed"] = pr["number"] in reviewed_numbers
    return prs


def review_pull_request(db: Session, team_id: int, pr_number: int, current_user) -> PRReviewResult:
    owner, repo_name, token = _get_repo_and_leader_token(db, team_id, current_user)

    files = github_service.get_pr_files(token, owner, repo_name, pr_number)
    prs = github_service.list_pull_requests(token, owner, repo_name)
    pr_meta = next((p for p in prs if p["number"] == pr_number), None)
    pr_title = pr_meta["title"] if pr_meta else f"PR #{pr_number}"

    result = ai_review_service.review_pr_diff(pr_number, pr_title, files)
    ai_review_service.save_pr_review(db, team_id, current_user.id, result)
    return result


def get_pr_review_history(db: Session, team_id: int, pr_number: int, current_user) -> PRReviewResult:
    if not team_repository.is_student_in_team(db, team_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'etes pas membre de cette equipe")

    saved = (
        db.query(PullRequestReview)
        .filter(PullRequestReview.team_id == team_id, PullRequestReview.pr_number == pr_number)
        .first()
    )
    if saved is None:
        raise HTTPException(status_code=404, detail="Aucune review sauvegardee pour cette PR")

    return PRReviewResult(
        pr_number=saved.pr_number,
        pr_title=saved.pr_title,
        files=saved.files,
        overall_quality_score=saved.overall_quality_score,
        summary=saved.summary,
        recurring_issues=saved.recurring_issues,
        critical_count=saved.critical_count,
        high_count=saved.high_count,
        medium_count=saved.medium_count,
        low_count=saved.low_count,
    )    