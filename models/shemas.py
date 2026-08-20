from pydantic import BaseModel, Field

#post
class SearchCreate(BaseModel):
    url: str
    maxItems: int = Field(default=10, ge=1)

class SearchCreateResponse(BaseModel):
    search_id: int 
    status: str 

#get
class OfferResponse(BaseModel):
    id: int 
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

class SearchResponse(BaseModel):
    search_id: int
    status: str
    count: int
    offers: list[OfferResponse] | None = None
    error: str | None = None