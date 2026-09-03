from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
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
    github_username: Optional[str] = None
    github_linked: bool = False


class MyTeamOut(BaseModel):
    """Reponse complete pour la page 'My Team' cote etudiant."""
    team_id: int
    team_name: str
    class_name: str
    leader: Optional[TeamMemberInfo] = None
    members: List[TeamMemberInfo]
    repository: Optional[RepositoryOut] = None
    my_team_role: str  # "LEADER" ou "MEMBER"


class MemberContribution(BaseModel):
    student_id: int
    first_name: str
    last_name: str
    github_username: Optional[str] = None
    linked: bool
    commits: int
    pull_requests: int
    percentage: float


class TeamContributionsOut(BaseModel):
    total_commits: int
    total_pull_requests: int
    contributions: List[MemberContribution]


class ActivityEventOut(BaseModel):
    type: str  # "push" | "pr_opened" | "pr_merged" | "issue_opened"
    actor_name: str
    actor_initials: str
    description: str
    created_at: datetime


class TeamSummaryOut(BaseModel):
    id: int
    name: str
    member_count: int
    repository_connected: bool


class TeamProjectDetailsOut(BaseModel):
    team_id: int
    team_name: str
    class_name: str
    repository: Optional[RepositoryOut] = None
    members: List[TeamMemberInfo]
    total_commits: int
    total_pull_requests: int    