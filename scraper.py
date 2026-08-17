"""
Scraper d'offres d'emploi Rekrute avec rotation de proxies (version corrigée).
Voir la réponse dans le chat pour le détail de chaque correctif (repérable ici par "FIX:").
"""

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import utils

def get_jobs(listing_url, maxItems=10): 
    url=listing_url
    proxy_list = utils.initialize_proxy_list()
    if not proxy_list:
        print("Aucun proxy chargé depuis free-proxy-list.txt.")
        return []

    offers = []
    proxy_index = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # FIX: un seul navigateur pour toute la session
        try:
            while True:
                print(f" ------- listing url: {url}------- ")
                listing_html, proxy_index = utils.fetch_with_retries(
                    browser, url, proxy_list, wait_selector="div.content-column", start_index=proxy_index
                )
                if not listing_html:
                    print("Impossible de charger la page de listing avec les proxies disponibles.")
                    raise Exception("All proxies failed")
                listing_soup = BeautifulSoup(listing_html, "html.parser")
                posts = listing_soup.find_all("li", class_="post-id")
                print(f" ------- {len(posts)} offres trouvées sur la page de listing ------- ")

                for post in posts:
                    if len(offers) >= maxItems:
                        break
                    link = utils.get_link(post)
                    if not link:
                        print(" ------- Lien introuvable pour une offre, on passe ------- ")
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
                        print(f""" ------- OK 
                            link: {link} \n
                            titre: {offer["titre"]} \n
                            sector: {offer["sector"]} \n
                            experience: {offer["experience"]} \n
                            region: {offer["region"]} \n
                            formation: {offer["formation"]} \n
                            competences personelles:{offer["competencesPersonnelles"]} \n
                            contrat: {offer["contrat"]} \n
                            teletravail: {offer["teletravail"]} \n
                            dateLimite: {offer["dateLimite"]} \n
                            description: {offer["description"]}
                        -------""")
                        offers.append(offer)
                    else: 
                        print(f" ------- html not founded for link : {link}")
                if len(offers) >= maxItems:
                    break
                next_page = listing_soup.find("a", class_="next")
                if next_page and next_page.get("href"):
                    url = f"https://www.rekrute.com{next_page.get("href")}"
                    continue
                break                   
        finally:
            browser.close()  # FIX: fermeture propre, plus de fuite de navigateurs
    return offers

if __name__ == "__main__":
    get_jobs("https://www.rekrute.com/fr/offres-emploi-informatique-electronique-fonction-13.html")