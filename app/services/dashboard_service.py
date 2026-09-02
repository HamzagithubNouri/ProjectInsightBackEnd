from datetime import datetime, timedelta, timezone

from github import Github
from fastapi import HTTPException

from app.repositories import team_repository, github_repo_repository, user_repository


def _extract_owner_repo(github_url: str) -> str:
    return github_url.rstrip("/").replace("https://github.com/", "").replace("http://github.com/", "")


def get_weekly_activity(db, current_user):
    """Commits des 7 derniers jours (aujourd'hui inclus) de l'utilisateur courant
    sur le repo de son equipe, jour par jour. Utilise le token du Team Leader
    pour l'appel API (meme logique que team_contribution_service), filtre sur
    le login GitHub de l'utilisateur courant."""
    team = team_repository.get_team_by_student(db, current_user.id)
    if team is None:
        raise HTTPException(status_code=404, detail="Vous n'etes assigne a aucune equipe")

    repo_record = github_repo_repository.get_repository_by_team(db, team.id)
    if repo_record is None:
        raise HTTPException(status_code=404, detail="Aucun repository connecte pour cette equipe")

    if not current_user.github_username:
        raise HTTPException(
            status_code=400,
            detail="Connectez votre compte GitHub pour voir votre activite",
        )

    if team.leader_id is None:
        raise HTTPException(status_code=400, detail="Cette equipe n'a pas de Team Leader assigne")

    leader = user_repository.get_user_by_id(db, team.leader_id)
    if leader is None or not leader.github_access_token:
        raise HTTPException(
            status_code=400,
            detail="Le Team Leader doit connecter son compte GitHub pour afficher l'activite",
        )

    today = datetime.now(timezone.utc).date()
    start_date = today - timedelta(days=6)
    since = datetime.combine(start_date, datetime.min.time(), tzinfo=timezone.utc)

    counts = {start_date + timedelta(days=i): 0 for i in range(7)}

    gh = Github(leader.github_access_token)
    try:
        gh_repo = gh.get_repo(_extract_owner_repo(repo_record.github_url))
        commits = gh_repo.get_commits(author=current_user.github_username, since=since)
        for c in commits:
            commit_date = c.commit.author.date.date()
            if commit_date in counts:
                counts[commit_date] += 1
    except Exception:
        pass  # repo inaccessible ou pas encore de commits -> compteurs a 0

    return [
        {
            "day": (start_date + timedelta(days=i)).strftime("%a"),
            "date": (start_date + timedelta(days=i)).isoformat(),
            "commits": counts[start_date + timedelta(days=i)],
        }
        for i in range(7)
    ]