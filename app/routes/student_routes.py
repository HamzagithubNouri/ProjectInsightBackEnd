from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.ai_review_schema import PRReviewResult
from app.services import ai_review_service
from app.database import get_db
from app.schemas.repository_schema import RepositoryConnect, RepositoryOut
from app.schemas.ai_review_schema import PRReviewResult
from app.schemas.team_schema import MyTeamOut, TeamContributionsOut
from app.schemas.github_schema import GithubConnectUrl, GithubStatusOut, GithubRepoOut, GithubBranchOut
from app.services import student_service, github_service, team_contribution_service
from app.auth.dependencies import require_role, get_current_user
from app.schemas.team_schema import ActivityEventOut
from app.services import dashboard_service
from app.schemas.dashboard_schema import ActivityDayOut, RecentFindingOut
router = APIRouter(
    prefix="/student",
    tags=["Etudiant"],
    dependencies=[Depends(require_role("student"))],
)


@router.get("/team", response_model=MyTeamOut)
def get_my_team(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return student_service.get_my_team(db, current_user)


@router.get("/team/contributions", response_model=TeamContributionsOut)
def get_team_contributions(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Vraies contributions (commits + PRs) par membre, calculees en direct
    depuis l'API GitHub et attribuees via github_username. Un membre sans
    compte GitHub lie apparait avec commits=0, linked=False."""
    return team_contribution_service.get_team_contributions(db, current_user)

@router.get("/dashboard/activity", response_model=list[ActivityDayOut])
def get_weekly_activity(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return dashboard_service.get_weekly_activity(db, current_user)


@router.get("/dashboard/recent-findings", response_model=list[RecentFindingOut])
def get_recent_findings(
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return student_service.get_recent_findings(db, current_user.id, limit)



@router.get("/team/activity", response_model=list[ActivityEventOut])
def get_team_activity(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return team_contribution_service.get_team_activity(db, current_user, limit)


@router.post("/teams/{team_id}/repository", response_model=RepositoryOut)
def connect_repository(
    team_id: int,
    data: RepositoryConnect,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Reserve au Team Leader (verifie dans le service)."""
    return student_service.connect_repository(db, team_id, data, current_user)


@router.get("/teams/{team_id}/repository", response_model=RepositoryOut)
def view_repository(
    team_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Lecture seule, accessible a tout membre de l'equipe."""
    return student_service.get_repository(db, team_id, current_user)


# --- GitHub OAuth : connexion du compte personnel de l'etudiant ---

@router.get("/github/connect", response_model=GithubConnectUrl)
def github_connect(current_user=Depends(get_current_user)):
    """Angular recupere cette URL puis fait window.location.href = authorize_url."""
    url = github_service.initiate_connect(current_user)
    return GithubConnectUrl(authorize_url=url)


@router.get("/github/status", response_model=GithubStatusOut)
def github_status(current_user=Depends(get_current_user)):
    return github_service.get_status(current_user)


@router.post("/github/disconnect")
def github_disconnect(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    github_service.disconnect(db, current_user)
    return {"detail": "Compte GitHub deconnecte"}


@router.get("/github/repos", response_model=list[GithubRepoOut])
def github_list_repos(current_user=Depends(get_current_user)):
    return github_service.list_repos(current_user)


@router.get("/github/repos/{owner}/{repo_name}/branches", response_model=list[GithubBranchOut])
def github_list_branches(owner: str, repo_name: str, current_user=Depends(get_current_user)):
    return github_service.list_branches(current_user, owner, repo_name)




@router.get("/teams/{team_id}/pulls")
def list_team_pull_requests(team_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return student_service.list_team_pull_requests(db, team_id, current_user)


@router.get("/teams/{team_id}/pr/{pr_number}/review", response_model=PRReviewResult)
def review_pull_request(team_id: int, pr_number: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return student_service.review_pull_request(db, team_id, pr_number, current_user)


@router.get("/teams/{team_id}/pr/{pr_number}/review-history", response_model=PRReviewResult)
def get_pr_review_history(team_id: int, pr_number: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return student_service.get_pr_review_history(db, team_id, pr_number, current_user)