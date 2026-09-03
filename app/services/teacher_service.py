from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.schemas.user import StudentCreate
from app.schemas.class_schema import ClassCreate, ClassSummaryOut, ClassDetailOut
from app.schemas.team_schema import TeamCreate, TeamSummaryOut, TeamProjectDetailsOut, TeamMemberInfo
from app.schemas.ai_review_schema import PRSummaryOut, PRReviewResult
from app.repositories import user_repository, class_repository, team_repository, github_repo_repository
from app.models.user import User
from app.models.pull_request_review import PullRequestReview
from app.auth.security import hash_password
from app.services import github_service, team_contribution_service

def create_student(db: Session, data: StudentCreate) -> User:
    existing = user_repository.get_user_by_email(db, data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Cet email est deja utilise")

    school_class = class_repository.get_class_by_id(db, data.class_id)
    if school_class is None:
        raise HTTPException(status_code=404, detail="Classe introuvable")

    student = User(
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        hashed_password=hash_password(data.password),
        role="student",
        school_class_id=data.class_id,
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


def create_class(db: Session, data: ClassCreate, teacher_id: int):
    return class_repository.create_class(db, data, teacher_id)


def create_team(db: Session, data: TeamCreate):
    if data.leader_id is not None and data.member_ids:
        if data.leader_id not in data.member_ids:
            raise HTTPException(
                status_code=400,
                detail="Le leader selectionne doit faire partie des membres de l'equipe",
            )

    team = team_repository.create_team(db, data.name, data.class_id)

    if data.member_ids:
        team_repository.add_members_bulk(db, team.id, data.member_ids)

    if data.leader_id is not None:
        team = team_repository.set_leader(db, team.id, data.leader_id)

    return team


def add_team_member(db: Session, team_id: int, student_id: int):
    return team_repository.add_member(db, team_id, student_id)


def get_my_classes(db: Session, teacher_id: int) -> list[ClassSummaryOut]:
    classes = class_repository.get_classes_by_teacher(db, teacher_id)
    return [
        ClassSummaryOut(
            id=c.id,
            name=c.name,
            student_count=len(user_repository.list_students(db, c.id)),
            team_count=len(team_repository.get_teams_by_class(db, c.id)),
        )
        for c in classes
    ]


def _require_class_owner(db: Session, class_id: int, current_user):
    school_class = class_repository.get_class_by_id(db, class_id)
    if school_class is None:
        raise HTTPException(status_code=404, detail="Classe introuvable")
    if school_class.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cette classe ne vous appartient pas")
    return school_class


def get_class_detail(db: Session, class_id: int, current_user) -> ClassDetailOut:
    school_class = _require_class_owner(db, class_id, current_user)
    teams = team_repository.get_teams_by_class(db, class_id)

    team_summaries = [
        TeamSummaryOut(
            id=team.id,
            name=team.name,
            member_count=len(team_repository.get_team_members(db, team.id)),
            repository_connected=github_repo_repository.get_repository_by_team(db, team.id) is not None,
        )
        for team in teams
    ]

    return ClassDetailOut(
        id=school_class.id,
        name=school_class.name,
        student_count=len(user_repository.list_students(db, class_id)),
        team_count=len(teams),
        teams=team_summaries,
    )


def _require_team_owner(db: Session, team_id: int, current_user):
    """Le prof doit etre proprietaire de la CLASSE a laquelle appartient l'equipe."""
    team = team_repository.get_team_by_id(db, team_id)
    if team is None:
        raise HTTPException(status_code=404, detail="Equipe introuvable")
    if team.school_class.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cette equipe ne vous appartient pas")
    return team


def get_team_project_details(db: Session, team_id: int, current_user) -> TeamProjectDetailsOut:
    team = _require_team_owner(db, team_id, current_user)

    member_rows = team_repository.get_team_members(db, team.id)
    members = [
        TeamMemberInfo(
            id=row.student.id,
            first_name=row.student.first_name,
            last_name=row.student.last_name,
            email=row.student.email,
            is_leader=(row.student.id == team.leader_id),
            github_username=row.student.github_username,
            github_linked=row.student.github_username is not None,
        )
        for row in member_rows
    ]

    repo = github_repo_repository.get_repository_by_team(db, team.id)
    total_commits, total_prs = team_contribution_service.get_team_github_totals(db, team.id)

    return TeamProjectDetailsOut(
        team_id=team.id,
        team_name=team.name,
        class_name=team.school_class.name,
        repository=repo,
        members=members,
        total_commits=total_commits,
        total_pull_requests=total_prs,
    )


def _get_repo_and_leader_token_for_teacher(db: Session, team_id: int, current_user):
    team = _require_team_owner(db, team_id, current_user)
    repo = github_repo_repository.get_repository_by_team(db, team_id)
    if repo is None:
        raise HTTPException(status_code=404, detail="Aucun repository connecte pour cette equipe")
    if team.leader_id is None:
        raise HTTPException(status_code=400, detail="Cette equipe n'a pas de Team Leader assigne")

    leader = user_repository.get_user_by_id(db, team.leader_id)
    if leader is None or not leader.github_access_token:
        raise HTTPException(status_code=400, detail="Le Team Leader n'a pas connecte son compte GitHub")

    owner, repo_name = repo.github_url.rstrip("/").replace("https://github.com/", "").split("/")
    return owner, repo_name, leader.github_access_token


def list_team_prs(db: Session, team_id: int, current_user) -> list[PRSummaryOut]:
    owner, repo_name, token = _get_repo_and_leader_token_for_teacher(db, team_id, current_user)
    prs = github_service.list_pull_requests(token, owner, repo_name)

    saved_reviews = {
        row.pr_number: row
        for row in db.query(PullRequestReview).filter(PullRequestReview.team_id == team_id).all()
    }

    return [
        PRSummaryOut(
            number=pr["number"],
            title=pr["title"],
            state=pr["state"],
            already_reviewed=pr["number"] in saved_reviews,
            quality_score=(saved_reviews[pr["number"]].overall_quality_score if pr["number"] in saved_reviews else None),
            reviewed_at=(saved_reviews[pr["number"]].reviewed_at if pr["number"] in saved_reviews else None),
        )
        for pr in prs
    ]

def get_team_pr_review(db: Session, team_id: int, pr_number: int, current_user) -> PRReviewResult:
    """Lecture seule : ne declenche JAMAIS de nouvelle analyse LangChain,
    contrairement au flux etudiant."""
    _require_team_owner(db, team_id, current_user)

    saved = (
        db.query(PullRequestReview)
        .filter(PullRequestReview.team_id == team_id, PullRequestReview.pr_number == pr_number)
        .first()
    )
    if saved is None:
        raise HTTPException(status_code=404, detail="Aucune review sauvegardee pour cette PR")

    return PRReviewResult(
        pr_number=saved.pr_number,
        pr_title=saved.pr_title,
        files=saved.files,
        overall_quality_score=saved.overall_quality_score,
        summary=saved.summary,
        recurring_issues=saved.recurring_issues,
        critical_count=saved.critical_count,
        high_count=saved.high_count,
        medium_count=saved.medium_count,
        low_count=saved.low_count,
    )