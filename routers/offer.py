from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.offer import get_jobs
import logging

logging.basicConfig(level=logging.DEBUG)

router = APIRouter(tags=["offers"])

@router.post('/api/search')
def get_jobs_data(scrap):
    try:
        jobs = get_jobs(scrap.url, scrap.maxItems) 

        return {
            "success": True,
            "count": len(jobs),
            "jobs": jobs
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
