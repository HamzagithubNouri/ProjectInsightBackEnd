from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.models import user, school_class, team, team_member, github_repository  # noqa: F401
from app.routes import auth_routes, admin_routes, teacher_routes, student_routes, ai_review_routes

Base.metadata.create_all(bind=engine)

app = FastAPI(title="ProjectInsight AI - Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # adresse par defaut d'Angular en dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(admin_routes.router)
app.include_router(teacher_routes.router)
app.include_router(student_routes.router)
app.include_router(ai_review_routes.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
