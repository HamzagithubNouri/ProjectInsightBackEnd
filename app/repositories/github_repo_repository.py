from sqlalchemy.orm import Session

from app.models.github_repository import GithubRepository


def connect_repository(db: Session, team_id: int, data, connected_by: int) -> GithubRepository:
    existing = db.query(GithubRepository).filter(GithubRepository.team_id == team_id).first()
    if existing:
        # deja un repo connecte pour cette equipe -> on le met a jour plutot que d'en creer un 2e
        existing.github_url = data.github_url
        existing.branch = data.branch
        existing.github_username = data.github_username
        existing.connected_by = connected_by
        existing.status = "connected"
        db.commit()
        db.refresh(existing)
        return existing

    repo = GithubRepository(
        team_id=team_id,
        github_url=data.github_url,
        branch=data.branch,
        github_username=data.github_username,
        connected_by=connected_by,
        status="connected",
    )
    db.add(repo)
    db.commit()
    db.refresh(repo)
    return repo


def get_repository_by_team(db: Session, team_id: int):
    return db.query(GithubRepository).filter(GithubRepository.team_id == team_id).first()  
    
