from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import utils
import logging 

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