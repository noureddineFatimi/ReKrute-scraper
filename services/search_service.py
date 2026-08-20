from models.schemas import SearchCreate, SearchCreateResponse
from database import get_session
from models.database import SearchJob
from datetime import datetime
from config import PENDING
import threading
import logging 
from database import get_session
from models.database import Offer, SearchJob
from config import FAILED, DONE
from fastapi import HTTPException
from sqlmodel import select
from models.schemas import SearchResponse, OfferResponse
from scraper.rekrute import get_jobs

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

def run_scraping(search_id: int):
    """
    Fonction exécutée dans le thread.
    Elle récupère le SearchJob, lance le scraper,
    sauvegarde les offres et met à jour le statut.
    """

    with get_session() as session:

        search = session.get(SearchJob, search_id)

        if search is None:
            logging.error(
                "SearchJob %s introuvable",
                search_id
            )
            return

        try:
            logging.info(
                "Début du scraping pour search_id=%s",
                search_id
            )

            offers = get_jobs(
                search.url,
                search.max_items
            )

            logging.info(
                "%d offres récupérées pour search_id=%s",
                len(offers),
                search_id
            )

            for offer_data in offers:

                offer = Offer(
                    search_id=search_id,
                    titre=offer_data.get("titre"),
                    link=offer_data.get("link"),
                    sector=offer_data.get("sector"),
                    experience=offer_data.get("experience"),
                    region=offer_data.get("region"),
                    formation=offer_data.get("formation"),
                    competencesPersonnelles=offer_data.get(
                        "competencesPersonnelles"
                    ),
                    contrat=offer_data.get("contrat"),
                    teletravail=offer_data.get("teletravail"),
                    description=offer_data.get("description"),
                    dateLimite=offer_data.get("dateLimite"),
                )

                session.add(offer)

            search.status = DONE
            search.error = None

            session.commit()

            logging.info(
                "Scraping terminé pour search_id=%s",
                search_id
            )

        except Exception as e:

            logging.exception(
                "Erreur pendant le scraping search_id=%s",
                search_id
            )

            search.status = FAILED
            search.error = str(e)

            session.commit()

def get_jobs_by_search_id(search_id):
    with get_session() as session:
        search = session.get(SearchJob, search_id)
        if search is None:
            raise HTTPException(
                status_code=404,
                detail="Search not found"
            )
        
        statement = select(Offer).where(
            Offer.search_id == search_id
        )

        offers = session.exec(statement).all()

        count = len(offers)

        offersResponseList: list[OfferResponse] = [OfferResponse(**offer.__dict__) for offer in offers]

        searchResponse = SearchResponse(search_id=search.id, status=search.status, count=count, offers=offersResponseList, error=search.error)
        return searchResponse
        