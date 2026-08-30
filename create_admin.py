"""
A executer UNE SEULE FOIS, manuellement, pour creer le tout premier compte Admin.
Ensuite, cet Admin cree les enseignants via l'API (POST /admin/teachers),
et les enseignants creent les etudiants (POST /teacher/students).

Usage :
    python create_admin.py
"""

from app.database import SessionLocal, engine, Base
from app.models import user, school_class, team, team_member, github_repository, review_history  # noqa: F401
from app.models.user import User
from app.auth.security import hash_password

Base.metadata.create_all(bind=engine)

db = SessionLocal()

print("--- Creation du compte Admin ---")
first_name = input("Prenom : ")
last_name = input("Nom : ")
email = input("Email : ")
password = input("Mot de passe : ")

existing = db.query(User).filter(User.email == email).first()
if existing:
    print(f"Un utilisateur avec l'email {email} existe deja. Rien n'a ete cree.")
else:
    admin = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        hashed_password=hash_password(password),
        role="admin",
    )
    db.add(admin)
    db.commit()
    print(f"Compte Admin cree avec succes : {email}")

db.close()
