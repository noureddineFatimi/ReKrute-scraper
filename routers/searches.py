from fastapi import APIRouter, HTTPException
import logging
from models.schemas import SearchCreate, SearchCreateResponse
from services.search_service import create_search, get_jobs_by_search_id
from models.schemas import SearchResponse

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

@router.get("/{search_id}", response_model=SearchResponse)
def get_jobs_data_by_search_id(search_id: int):
    try:
        searchResponse = get_jobs_by_search_id(search_id=search_id)
        return searchResponse
    except HTTPException as httpex:
            raise HTTPException(
                status_code=httpex.status_code,
                detail=str(httpex)
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )