from github import Github
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.auth import github_oauth
from app.schemas.github_schema import GithubRepoOut, GithubBranchOut, GithubStatusOut


def initiate_connect(current_user) -> str:
    """Genere l'URL vers laquelle Angular doit rediriger le navigateur
    (window.location.href = cette url)."""
    state = github_oauth.generate_state_for_user(current_user.id)
    return github_oauth.build_authorize_url(state)


def handle_callback(db: Session, code: str, state: str):
    """Appele par GitHub (redirection navigateur) apres que l'utilisateur
    ait accepte l'autorisation. Retrouve QUEL utilisateur a initie la
    demande via le 'state', puis sauvegarde son token."""
    from app.repositories.user_repository import get_user_by_id  # import local pour eviter les cycles

    user_id = github_oauth.pop_user_id_for_state(state)
    if user_id is None:
        raise HTTPException(status_code=400, detail="State invalide ou expire")

    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    access_token = github_oauth.exchange_code_for_token(code)
    username = github_oauth.get_github_username(access_token)

    user.github_access_token = access_token
    user.github_username = username
    db.commit()

    return user


def get_status(current_user) -> GithubStatusOut:
    return GithubStatusOut(
        connected=current_user.github_access_token is not None,
        github_username=current_user.github_username,
    )


def disconnect(db: Session, current_user):
    current_user.github_access_token = None
    current_user.github_username = None
    db.commit()


def _require_connected(current_user) -> str:
    if not current_user.github_access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Compte GitHub non connecte. Connectez-vous a GitHub d'abord.",
        )
    return current_user.github_access_token


def list_repos(current_user) -> list[GithubRepoOut]:
    token = _require_connected(current_user)
    gh = Github(token)
    repos = []
    for repo in gh.get_user().get_repos():
        repos.append(
            GithubRepoOut(
                full_name=repo.full_name,
                private=repo.private,
                default_branch=repo.default_branch,
            )
        )
    return repos


def list_branches(current_user, owner: str, repo_name: str) -> list[GithubBranchOut]:
    token = _require_connected(current_user)
    gh = Github(token)
    try:
        repo = gh.get_repo(f"{owner}/{repo_name}")
    except Exception:
        raise HTTPException(status_code=404, detail="Repository introuvable ou inaccessible")

    return [GithubBranchOut(name=b.name) for b in repo.get_branches()]

def _extract_owner_repo_from_url(github_url: str) -> str:
    """'https://github.com/team-alpha/library-mgmt-system' -> 'team-alpha/library-mgmt-system'"""
    return github_url.rstrip("/").replace("https://github.com/", "").replace("http://github.com/", "")


def get_pr_files(current_user, team_id: int, pr_number: int, db):
    """Recupere les fichiers modifies d'une PR pour le repo de l'equipe, en utilisant
    le token GitHub du Team Leader (meme principe que team_contribution_service)."""
    from app.repositories import team_repository, github_repo_repository, user_repository

    team = team_repository.get_team_by_id(db, team_id)
    if team is None:
        raise HTTPException(status_code=404, detail="Equipe introuvable")

    if not team_repository.is_student_in_team(db, team_id, current_user.id):
        raise HTTPException(status_code=403, detail="Vous n'etes pas membre de cette equipe")

    repo_record = github_repo_repository.get_repository_by_team(db, team_id)
    if repo_record is None:
        raise HTTPException(status_code=404, detail="Aucun repository connecte pour cette equipe")

    if team.leader_id is None:
        raise HTTPException(status_code=400, detail="Cette equipe n'a pas de Team Leader assigne")

    leader = user_repository.get_user_by_id(db, team.leader_id)
    if leader is None or not leader.github_access_token:
        raise HTTPException(
            status_code=400,
            detail="Le Team Leader doit connecter son compte GitHub pour analyser les PR",
        )

    gh = Github(leader.github_access_token)
    try:
        gh_repo = gh.get_repo(_extract_owner_repo_from_url(repo_record.github_url))
        pr = gh_repo.get_pull(pr_number)
    except Exception:
        raise HTTPException(status_code=404, detail="Pull Request introuvable ou inaccessible")

    files = [{"filename": f.filename, "patch": f.patch or ""} for f in pr.get_files()]

    return pr.number, pr.title, files