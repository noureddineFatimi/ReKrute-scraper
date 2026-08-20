from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.offer import get_jobs, get_jobs_by_search_id
import logging
from models.shemas import SearchResponse

logging.basicConfig(level=logging.DEBUG)

router = APIRouter(
    prefix="/offers",
    tags=["Offers"]
)

@router.get("/{search_id}", response_model=SearchResponse)
def get_jobs_data(search_id: int):
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