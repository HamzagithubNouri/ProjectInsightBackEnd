from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.repository_schema import RepositoryConnect, RepositoryOut
from app.schemas.team_schema import MyTeamOut
from app.services import student_service
from app.auth.dependencies import require_role, get_current_user

router = APIRouter(
    prefix="/student",
    tags=["Etudiant"],
    dependencies=[Depends(require_role("student"))],
)


@router.get("/team", response_model=MyTeamOut)
def get_my_team(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Page 'My Team' : infos equipe + classe + leader + membres + repo +
    mon role (LEADER/MEMBER) dans cette equipe -> utilise par Angular pour
    afficher ou masquer l'item de navigation 'Repository'."""
    return student_service.get_my_team(db, current_user)


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
