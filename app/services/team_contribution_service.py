from github import Github
from fastapi import HTTPException

from app.repositories import team_repository, github_repo_repository, user_repository
from app.schemas.team_schema import MemberContribution, TeamContributionsOut

# Securite MVP : on ne compte pas plus de N pull requests pour eviter un
# appel trop long sur un tres gros repo (l'API GitHub pagine, chaque page
# est un appel reseau). A retirer ou augmenter si besoin plus tard.
MAX_PULL_REQUESTS_SCANNED = 200


def _extract_owner_repo(github_url: str) -> str:
    """'https://github.com/team-alpha/library-mgmt-system' -> 'team-alpha/library-mgmt-system'"""
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

    # --- Commits par login GitHub (l'API donne deja le total agrege) ---
    commits_by_login: dict[str, int] = {}
    try:
        for contributor in gh_repo.get_contributors():
            commits_by_login[contributor.login] = contributor.contributions
    except Exception:
        pass  # repo tout neuf sans commits : on continue avec un dict vide

    # --- Pull requests par login GitHub (comptees manuellement, plafonnees) ---
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
