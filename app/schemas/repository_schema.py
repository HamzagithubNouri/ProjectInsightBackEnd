from datetime import datetime
from pydantic import BaseModel


class RepositoryConnect(BaseModel):
    github_url: str
    branch: str = "main"
    github_username: str | None = None


class RepositoryOut(BaseModel):
    id: int
    team_id: int
    github_url: str
    branch: str
    github_username: str | None = None
    status: str
    connected_at: datetime

    class Config:
        from_attributes = True
