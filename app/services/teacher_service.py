from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.schemas.user import StudentCreate
from app.schemas.class_schema import ClassCreate
from app.schemas.team_schema import TeamCreate
from app.repositories import user_repository, class_repository, team_repository
from app.models.user import User
from app.auth.security import hash_password


def create_student(db: Session, data: StudentCreate) -> User:
    existing = user_repository.get_user_by_email(db, data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Cet email est deja utilise")

    school_class = class_repository.get_class_by_id(db, data.class_id)
    if school_class is None:
        raise HTTPException(status_code=404, detail="Classe introuvable")

    student = User(
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        hashed_password=hash_password(data.password),
        role="student",
        school_class_id=data.class_id,
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


def create_class(db: Session, data: ClassCreate, teacher_id: int):
    return class_repository.create_class(db, data, teacher_id)


def create_team(db: Session, data: TeamCreate):
    if data.leader_id is not None and data.member_ids:
        if data.leader_id not in data.member_ids:
            raise HTTPException(
                status_code=400,
                detail="Le leader selectionne doit faire partie des membres de l'equipe",
            )

    team = team_repository.create_team(db, data.name, data.class_id)

    if data.member_ids:
        team_repository.add_members_bulk(db, team.id, data.member_ids)

    if data.leader_id is not None:
        team = team_repository.set_leader(db, team.id, data.leader_id)

    return team


def add_team_member(db: Session, team_id: int, student_id: int):
    return team_repository.add_member(db, team_id, student_id)
