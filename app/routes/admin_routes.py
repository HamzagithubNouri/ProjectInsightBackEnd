from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import TeacherCreate, UserOut
from app.services import admin_service
from app.auth.dependencies import require_role

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(require_role("admin"))],  # protege TOUTES les routes de ce fichier
)


@router.post("/teachers", response_model=UserOut)
def create_teacher(data: TeacherCreate, db: Session = Depends(get_db)):
    return admin_service.create_teacher(db, data)
