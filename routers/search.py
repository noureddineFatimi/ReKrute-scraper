from fastapi import APIRouter, HTTPException
import logging
from models.shemas import SearchCreate, SearchCreateResponse
from services.search import create_search

logging.basicConfig(level=logging.DEBUG)

router = APIRouter(
    prefix="/searches",
    tags=["Searches"]
)

@router.post("", response_model=SearchCreateResponse)
def search(searchCreate: SearchCreate):
    try:
        searchCreateResponse = create_search(searchCreate=searchCreate)
        return searchCreateResponse
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )