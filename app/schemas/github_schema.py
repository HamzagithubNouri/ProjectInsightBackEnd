from typing import Optional
from pydantic import BaseModel


class GithubConnectUrl(BaseModel):
    authorize_url: str


class GithubStatusOut(BaseModel):
    connected: bool
    github_username: Optional[str] = None


class GithubRepoOut(BaseModel):
    full_name: str  # ex: "team-alpha/library-mgmt-system"
    private: bool
    default_branch: str


class GithubBranchOut(BaseModel):
    name: str
