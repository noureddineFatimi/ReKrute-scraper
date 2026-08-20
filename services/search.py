from models.shemas import SearchCreate, SearchCreateResponse
from database import engine, get_session
from models.database import SearchJob
from datetime import datetime
from config import PENDING
import threading
from offer import run_scraping

def start_scraping(search_id: int):
    """
    Lance le scraping dans un thread séparé.
    """

    thread = threading.Thread(
        target=run_scraping,
        args=(search_id,),
        daemon=True
    )

    thread.start()

def create_search(searchCreate: SearchCreate):
    with get_session() as session:
        search = SearchJob(url=searchCreate.url, max_items=searchCreate.maxItems, status=PENDING,created_at=datetime.now())
        session.add(search)
        session.commit()
        session.refresh(search)
        search_id = search.id
    start_scraping(search_id)
    searchCreateResponse = SearchCreateResponse(search_id=search_id, status=PENDING)
    return searchCreateResponse