from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.schemas.user import UserLogin
from app.repositories import user_repository
from app.auth.security import verify_password, create_access_token


def authenticate_user(db: Session, credentials: UserLogin) -> str:
    user = user_repository.get_user_by_email(db, credentials.email)
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
        )
    return create_access_token(data={"sub": user.email, "role": user.role})
