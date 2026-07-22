from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserLogin, Token, UserOut
from app.services import auth_service
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentification"])

# Pas de POST /register ici : les comptes sont crees en cascade
# (Admin -> cree les enseignants, Enseignant -> cree les etudiants).
# Voir admin_routes.py et teacher_routes.py, et create_admin.py pour le tout premier Admin.


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # OAuth2PasswordRequestForm utilise le champ "username" -> on y met l'email
    credentials = UserLogin(email=form_data.username, password=form_data.password)
    token = auth_service.authenticate_user(db, credentials)
    return Token(access_token=token)


@router.get("/me", response_model=UserOut)
def read_current_user(current_user=Depends(get_current_user)):
    return current_user
