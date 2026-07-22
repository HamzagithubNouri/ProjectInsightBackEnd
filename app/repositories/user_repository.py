from sqlalchemy.orm import Session

from app.models.user import User


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def list_students(db: Session, class_id: int | None = None):
    query = db.query(User).filter(User.role == "student")
    if class_id is not None:
        query = query.filter(User.school_class_id == class_id)
    return query.all()
