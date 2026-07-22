from sqlalchemy.orm import Session

from app.models.school_class import SchoolClass


def create_class(db: Session, data, teacher_id: int) -> SchoolClass:
    db_class = SchoolClass(
        name=data.name,
        course_code=data.course_code,
        year=data.year,
        max_students=data.max_students,
        teacher_id=teacher_id,
    )
    db.add(db_class)
    db.commit()
    db.refresh(db_class)
    return db_class


def get_class_by_id(db: Session, class_id: int):
    return db.query(SchoolClass).filter(SchoolClass.id == class_id).first()


def get_classes_by_teacher(db: Session, teacher_id: int):
    return db.query(SchoolClass).filter(SchoolClass.teacher_id == teacher_id).all()
