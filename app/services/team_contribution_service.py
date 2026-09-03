from datetime import datetime

from github import Github
from fastapi import HTTPException

from app.repositories import team_repository, github_repo_repository, user_repository
from app.schemas.team_schema import MemberContribution, TeamContributionsOut

MAX_PULL_REQUESTS_SCANNED = 200


def _extract_owner_repo(github_url: str) -> str:
    return github_url.rstrip("/").replace("https://github.com/", "").replace("http://github.com/", "")


def get_team_contributions(db, current_user) -> TeamContributionsOut:
    team = team_repository.get_team_by_student(db, current_user.id)
    if team is None:
        raise HTTPException(status_code=404, detail="Vous n'etes assigne a aucune equipe")

    repo_record = github_repo_repository.get_repository_by_team(db, team.id)
    if repo_record is None:
        raise HTTPException(status_code=404, detail="Aucun repository connecte pour cette equipe")

    if team.leader_id is None:
        raise HTTPException(status_code=400, detail="Cette equipe n'a pas de Team Leader assigne")

    leader = user_repository.get_user_by_id(db, team.leader_id)
    if leader is None or not leader.github_access_token:
        raise HTTPException(
            status_code=400,
            detail="Le Team Leader doit connecter son compte GitHub pour recuperer les contributions",
        )

    gh = Github(leader.github_access_token)
    try:
        gh_repo = gh.get_repo(_extract_owner_repo(repo_record.github_url))
    except Exception:
        raise HTTPException(status_code=404, detail="Repository GitHub introuvable ou inaccessible")

    commits_by_login: dict[str, int] = {}
    try:
        for contributor in gh_repo.get_contributors():
            commits_by_login[contributor.login] = contributor.contributions
    except Exception:
        pass

    prs_by_login: dict[str, int] = {}
    try:
        scanned = 0
        for pr in gh_repo.get_pulls(state="all"):
            if pr.user is not None:
                prs_by_login[pr.user.login] = prs_by_login.get(pr.user.login, 0) + 1
            scanned += 1
            if scanned >= MAX_PULL_REQUESTS_SCANNED:
                break
    except Exception:
        pass

    total_commits = sum(commits_by_login.values())
    total_prs = sum(prs_by_login.values())

    member_rows = team_repository.get_team_members(db, team.id)
    contributions = []
    for row in member_rows:
        student = row.student
        username = student.github_username
        commits = commits_by_login.get(username, 0) if username else 0
        prs = prs_by_login.get(username, 0) if username else 0
        percentage = round((commits / total_commits * 100), 1) if total_commits > 0 else 0.0

        contributions.append(
            MemberContribution(
                student_id=student.id,
                first_name=student.first_name,
                last_name=student.last_name,
                github_username=username,
                linked=username is not None,
                commits=commits,
                pull_requests=prs,
                percentage=percentage,
            )
        )

    return TeamContributionsOut(
        total_commits=total_commits,
        total_pull_requests=total_prs,
        contributions=contributions,
    )


# --- Activity Timeline : commits + PR + issues, fusionnes et tries par date ---

def _initials(first_name: str, last_name: str) -> str:
    return f"{first_name[0]}{last_name[0]}".upper()


def _display_name(login_to_student: dict, login: str | None, fallback_name: str | None):
    student = login_to_student.get(login) if login else None
    if student:
        return f"{student.first_name} {student.last_name}", _initials(student.first_name, student.last_name)

    name = fallback_name or login or "Unknown"
    parts = name.split()
    initials = (parts[0][0] + parts[-1][0]).upper() if len(parts) >= 2 else name[:2].upper()
    return name, initials


def get_team_activity(db, current_user, limit: int = 10) -> list[dict]:
    team = team_repository.get_team_by_student(db, current_user.id)
    if team is None:
        raise HTTPException(status_code=404, detail="Vous n'etes assigne a aucune equipe")

    repo_record = github_repo_repository.get_repository_by_team(db, team.id)
    if repo_record is None:
        raise HTTPException(status_code=404, detail="Aucun repository connecte pour cette equipe")

    if team.leader_id is None:
        raise HTTPException(status_code=400, detail="Cette equipe n'a pas de Team Leader assigne")

    leader = user_repository.get_user_by_id(db, team.leader_id)
    if leader is None or not leader.github_access_token:
        raise HTTPException(
            status_code=400,
            detail="Le Team Leader doit connecter son compte GitHub pour afficher l'activite",
        )

    member_rows = team_repository.get_team_members(db, team.id)
    login_to_student = {
        row.student.github_username: row.student for row in member_rows if row.student.github_username
    }

    gh = Github(leader.github_access_token)
    try:
        gh_repo = gh.get_repo(_extract_owner_repo(repo_record.github_url))
    except Exception:
        raise HTTPException(status_code=404, detail="Repository GitHub introuvable ou inaccessible")

    events: list[dict] = []

    # --- Commits : commits consecutifs du meme auteur regroupes en un seul evenement ---
    try:
        commits = list(gh_repo.get_commits()[:30])
        i = 0
        while i < len(commits):
            c = commits[i]
            author_login = c.author.login if c.author else None
            fallback_name = c.commit.author.name if c.commit and c.commit.author else "Unknown"
            count = 1
            j = i + 1
            while j < len(commits) and (commits[j].author.login if commits[j].author else None) == author_login:
                count += 1
                j += 1

            name, initials = _display_name(login_to_student, author_login, fallback_name)
            events.append({
                "type": "push",
                "actor_name": name,
                "actor_initials": initials,
                "description": f"pushed {count} commit{'s' if count > 1 else ''} to {gh_repo.default_branch}",
                "created_at": c.commit.author.date if c.commit and c.commit.author else datetime.utcnow(),
            })
            i = j
    except Exception:
        pass

    # --- Pull requests ---
    try:
        for pr in list(gh_repo.get_pulls(state="all", sort="updated", direction="desc"))[:15]:
            login = pr.user.login if pr.user else None
            name, initials = _display_name(login_to_student, login, login)

            if pr.merged:
                events.append({
                    "type": "pr_merged",
                    "actor_name": name,
                    "actor_initials": initials,
                    "description": f"merged PR #{pr.number}: {pr.title}",
                    "created_at": pr.merged_at or pr.updated_at,
                })
            else:
                events.append({
                    "type": "pr_opened",
                    "actor_name": name,
                    "actor_initials": initials,
                    "description": f"opened PR #{pr.number}: {pr.title}",
                    "created_at": pr.created_at,
                })
    except Exception:
        pass

    # --- Issues (hors PR, qui apparaissent aussi comme issues cote API) ---
    try:
        for issue in list(gh_repo.get_issues(state="all", sort="updated", direction="desc"))[:15]:
            if issue.pull_request is not None:
                continue
            login = issue.user.login if issue.user else None
            name, initials = _display_name(login_to_student, login, login)
            events.append({
                "type": "issue_opened",
                "actor_name": name,
                "actor_initials": initials,
                "description": f"opened issue #{issue.number}: {issue.title}",
                "created_at": issue.created_at,
            })
    except Exception:
        pass

    events.sort(key=lambda e: e["created_at"], reverse=True)
    return events[:limit]



def get_team_github_totals(db, team_id: int) -> tuple[int, int]:
    """Version allegee, sans detail par membre : juste (total_commits, total_prs).
    Ne leve jamais d'exception, renvoie (0, 0) si repo/leader/token manquant —
    on ne veut pas qu'une erreur GitHub casse tout l'ecran Project Details."""
    repo_record = github_repo_repository.get_repository_by_team(db, team_id)
    if repo_record is None:
        return 0, 0

    team = team_repository.get_team_by_id(db, team_id)
    if team is None or team.leader_id is None:
        return 0, 0

    leader = user_repository.get_user_by_id(db, team.leader_id)
    if leader is None or not leader.github_access_token:
        return 0, 0

    gh = Github(leader.github_access_token)
    try:
        gh_repo = gh.get_repo(_extract_owner_repo(repo_record.github_url))
    except Exception:
        return 0, 0

    total_commits = 0
    try:
        for contributor in gh_repo.get_contributors():
            total_commits += contributor.contributions
    except Exception:
        pass

    total_prs = 0
    try:
        for _ in gh_repo.get_pulls(state="all"):
            total_prs += 1
            if total_prs >= MAX_PULL_REQUESTS_SCANNED:
                break
    except Exception:
        pass

    return total_commits, total_prs    