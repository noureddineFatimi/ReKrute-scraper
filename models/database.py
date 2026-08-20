from datetime import datetime
from sqlmodel import SQLModel, Field

class SearchJob(SQLModel, table=True):
    __tablename__ = "search_job"

    id: int | None = Field(default=None, primary_key=True)
    url: str
    max_items: int
    status: str
    created_at: datetime
    error: str | None = None

class Offer(SQLModel, table=True):
    __tablename__ = "offer"

    id: int | None = Field(default=None, primary_key=True)
    search_id: int = Field(foreign_key="search_job.id")

    titre: str | None = None
    link: str | None = None
    sector: str | None = None
    experience: str | None = None
    region: str | None = None
    formation: str | None = None
    competencesPersonnelles: str | None = None
    contrat: str | None = None
    teletravail: str | None = None
    description: str | None = None
    dateLimite: str | None = None