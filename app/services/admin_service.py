from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.schemas.user import TeacherCreate
from app.repositories import user_repository
from app.models.user import User
from app.auth.security import hash_password


def create_teacher(db: Session, data: TeacherCreate) -> User:
    existing = user_repository.get_user_by_email(db, data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Cet email est deja utilise")
    teacher = User(
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        hashed_password=hash_password(data.password),
        role="teacher",
    )
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    return teacher

def list_teachers(db: Session):
    return user_repository.list_teachers(db)


def delete_teacher(db: Session, teacher_id: int):
    teacher = user_repository.get_user_by_id(db, teacher_id)
    if teacher is None or teacher.role != "teacher":
        raise HTTPException(status_code=404, detail="Enseignant introuvable")
    user_repository.delete_user(db, teacher_id)    
