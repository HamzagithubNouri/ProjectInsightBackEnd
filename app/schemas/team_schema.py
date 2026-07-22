from typing import Optional, List
from pydantic import BaseModel

from app.schemas.repository_schema import RepositoryOut


class TeamCreate(BaseModel):
    name: str
    class_id: int
    member_ids: Optional[List[int]] = None
    leader_id: Optional[int] = None  # doit faire partie de member_ids si fourni


class TeamOut(BaseModel):
    id: int
    name: str
    class_id: int
    leader_id: Optional[int] = None

    class Config:
        from_attributes = True


class AddTeamMember(BaseModel):
    student_id: int


class TeamMemberInfo(BaseModel):
    """Un membre d'equipe avec son role calcule (pas stocke en base)."""
    id: int
    first_name: str
    last_name: str
    email: str
    is_leader: bool


class MyTeamOut(BaseModel):
    """Reponse complete pour la page 'My Team' cote etudiant."""
    team_id: int
    team_name: str
    class_name: str
    leader: Optional[TeamMemberInfo] = None
    members: List[TeamMemberInfo]
    repository: Optional[RepositoryOut] = None
    my_team_role: str  # "LEADER" ou "MEMBER"
