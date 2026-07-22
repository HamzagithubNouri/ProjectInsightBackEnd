from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TeacherCreate(BaseModel):
    """Utilise uniquement par l'Admin pour creer un compte enseignant."""
    first_name: str
    last_name: str
    email: EmailStr
    password: str


class StudentCreate(BaseModel):
    """Utilise uniquement par l'Enseignant pour creer un compte etudiant.
    Le prof choisit lui-meme le mot de passe initial et le communique
    a l'etudiant (meme logique que ESPRIT, sans le systeme d'email)."""
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    class_id: int


class UserOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    role: str
    school_class_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
