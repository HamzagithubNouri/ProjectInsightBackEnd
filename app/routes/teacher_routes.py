from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import StudentCreate, UserOut
from app.schemas.class_schema import ClassCreate, ClassOut, ClassSummaryOut, ClassDetailOut
from app.schemas.team_schema import TeamProjectDetailsOut
from app.schemas.ai_review_schema import PRSummaryOut, PRReviewResult
from app.schemas.team_schema import TeamCreate, TeamOut, AddTeamMember
from app.schemas.team_member_schema import TeamMemberOut
from app.services import teacher_service
from app.repositories import class_repository, team_repository, user_repository
from app.auth.dependencies import require_role, get_current_user

router = APIRouter(
    prefix="/teacher",
    tags=["Enseignant"],
    dependencies=[Depends(require_role("teacher"))],
)


@router.post("/students", response_model=UserOut)
def create_student(data: StudentCreate, db: Session = Depends(get_db)):
    return teacher_service.create_student(db, data)


@router.get("/students", response_model=list[UserOut])
def list_students(class_id: int | None = None, db: Session = Depends(get_db)):
    """Liste les etudiants. Passe ?class_id=X pour filtrer sur une classe
    (utilise par le dropdown 'Membres' de Create Team)."""
    return user_repository.list_students(db, class_id)


@router.post("/classes", response_model=ClassOut)
def create_class(
    data: ClassCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return teacher_service.create_class(db, data, current_user.id)


@router.get("/classes", response_model=list[ClassSummaryOut])
def list_my_classes(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return teacher_service.get_my_classes(db, current_user.id)

@router.post("/teams", response_model=TeamOut)
def create_team(data: TeamCreate, db: Session = Depends(get_db)):
    return teacher_service.create_team(db, data)


@router.get("/teams", response_model=list[TeamOut])
def list_teams(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return team_repository.get_teams_by_teacher(db, current_user.id)


@router.post("/teams/{team_id}/members", response_model=TeamMemberOut)
def add_member(team_id: int, data: AddTeamMember, db: Session = Depends(get_db)):
    return teacher_service.add_team_member(db, team_id, data.student_id)



@router.get("/classes/{class_id}", response_model=ClassDetailOut)
def get_class_detail(class_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return teacher_service.get_class_detail(db, class_id, current_user)


@router.get("/teams/{team_id}/details", response_model=TeamProjectDetailsOut)
def get_team_project_details(team_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return teacher_service.get_team_project_details(db, team_id, current_user)


@router.get("/teams/{team_id}/prs", response_model=list[PRSummaryOut])
def list_team_prs(team_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return teacher_service.list_team_prs(db, team_id, current_user)


@router.get("/teams/{team_id}/prs/{pr_number}/review", response_model=PRReviewResult)
def get_team_pr_review(team_id: int, pr_number: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return teacher_service.get_team_pr_review(db, team_id, pr_number, current_user)