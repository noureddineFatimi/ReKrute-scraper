from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import services.utils as utils
import logging 
from database import engine, get_session
from models.database import Offer, SearchJob
from config import FAILED, DONE
from fastapi import HTTPException
from sqlmodel import select
from models.shemas import SearchResponse, OfferResponse

def get_jobs(listing_url, maxItems=10): 
    url=listing_url
    proxy_list = utils.initialize_proxy_list()
    if not proxy_list:
        logging.error("Aucun proxy chargé depuis proxy-list.txt.")
        raise RuntimeError("Proxies required")

    offers = []
    proxy_index = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  
        try:
            while True:
                logging.info("listing url: %s", url)
                listing_html, proxy_index = utils.fetch_with_retries(
                    browser, url, proxy_list, wait_selector="div.content-column", start_index=proxy_index
                )
                if not listing_html:
                    logging.error("Impossible de charger la page de listing avec les proxies disponibles")
                    raise RuntimeError("All proxies failed")
                listing_soup = BeautifulSoup(listing_html, "html.parser")
                posts = listing_soup.find_all("li", class_="post-id")
                logging.info("%d offres trouvées sur la page de listing", len(posts))

                for post in posts:
                    if len(offers) >= maxItems:
                        break
                    link = utils.get_link(post)
                    if not link:
                        logging.warning("Lien introuvable pour une offre, on passe")
                        continue

                    html, proxy_index = utils.fetch_with_retries(
                        browser, link, proxy_list,
                        wait_selector="div.contentbloc div.listWrpService.jobdetail .row h1",
                        extract_selector="div.contentbloc",
                        start_index=proxy_index,
                    )

                    if html:
                        soup=BeautifulSoup(html, "html.parser")
                        offer=utils.create_new_offer(beautifulSoupHtml=soup, link=link)
                        logging.info(
                            "------- OK -------\n"
                            "link: %s\n"
                            "titre: %s\n"
                            "sector: %s\n"
                            "experience: %s\n"
                            "region: %s\n"
                            "formation: %s\n"
                            "competences personnelles: %s\n"
                            "contrat: %s\n"
                            "teletravail: %s\n"
                            "dateLimite: %s\n"
                            "description: %s\n"
                            "------------------",
                            link,
                            offer["titre"],
                            offer["sector"],
                            offer["experience"],
                            offer["region"],
                            offer["formation"],
                            offer["competencesPersonnelles"],
                            offer["contrat"],
                            offer["teletravail"],
                            offer["dateLimite"],
                            offer["description"],
                    )
                        offers.append(offer)
                    else: 
                        logging.warning("html not founded for link : %s", link)
                if len(offers) >= maxItems:
                    break
                next_page = listing_soup.find("a", class_="next")
                if next_page is not None and next_page.get("href") is not None:
                    url = f"https://www.rekrute.com{next_page.get('href')}"
                    continue
                break                   
        finally:
            browser.close()  
    return offers

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
        
