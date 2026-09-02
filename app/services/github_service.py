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

def list_pull_requests(token: str, owner: str, repo_name: str) -> list[dict]:
    gh = Github(token)
    try:
        repo = gh.get_repo(f"{owner}/{repo_name}")
    except Exception:
        raise HTTPException(status_code=404, detail="Repository introuvable ou inaccessible")

    prs = []
    for pr in repo.get_pulls(state="all"):
        prs.append({
            "number": pr.number,
            "title": pr.title,
            "state": "merged" if pr.merged else pr.state,  # "open" | "closed" | "merged"
            "author": pr.user.login if pr.user else None,
        })
    return prs


def get_pr_files(token: str, owner: str, repo_name: str, pr_number: int) -> list[dict]:
    gh = Github(token)
    try:
        repo = gh.get_repo(f"{owner}/{repo_name}")
        pr = repo.get_pull(pr_number)
    except Exception:
        raise HTTPException(status_code=404, detail="Pull Request introuvable")

    return [{"filename": f.filename, "patch": f.patch or ""} for f in pr.get_files()]    