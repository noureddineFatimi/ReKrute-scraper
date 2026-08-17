"""
Scraper d'offres d'emploi Rekrute avec rotation de proxies (version corrigée).
Voir la réponse dans le chat pour le détail de chaque correctif (repérable ici par "FIX:").
"""

import os
import time

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from config import USERNAME, PASSWORD

NAV_TIMEOUT = 20000  # proxies gratuits = souvent lents, 10s coupait trop court
DEBUG_DIR = "debug_dumps"  # screenshot + HTML sauvegardés ici quand wait_for_selector échoue
USERNAME = USERNAME
PASSWORD = PASSWORD

def initialize_proxy_list(path="proxy-list.txt"):
    """Charge les proxies, un par ligne (format ip:port ou host:port)."""
    proxy_list = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            proxy = line.strip()  # FIX: sans strip(), chaque proxy contenait un "\n" -> invalide
            if not proxy:
                continue
            if "://" not in proxy:
                proxy = f"http://{proxy}"
            proxy_list.append(proxy)
    return proxy_list


def get_link(post):
    """Extrait le lien complet de l'offre depuis un <li class='post-id'>."""
    tag = post.select_one(".titreJob")
    if tag and tag.get("href"):
        return f"https://www.rekrute.com{tag.get('href')}"
    return None


def _dump_debug(page, url):
    """Quand wait_for_selector échoue, sauvegarde une capture d'écran + le HTML brut pour voir
    EXACTEMENT ce que ce proxy a réellement chargé : bloqué ? CAPTCHA ? juste lent à finir
    de rendre ? page ok mais structure différente de celle attendue ?"""
    os.makedirs(DEBUG_DIR, exist_ok=True)
    stamp = int(time.time() * 1000)
    base = os.path.join(DEBUG_DIR, str(stamp))
    try:
        page.screenshot(path=f"{base}.png", full_page=True)
    except Exception:
        pass
    try:
        with open(f"{base}.html", "w", encoding="utf-8") as f:
            f.write(page.content())
    except Exception:
        pass
    print(f" ------- Debug sauvegardé : {base}.png / {base}.html (pour {url}) -------")


def fetch_html(browser, url, proxy, wait_selector, extract_selector=None, timeout=NAV_TIMEOUT):
    """
    Ouvre un context isolé (léger, pas un nouveau navigateur) avec `proxy`, charge `url`,
    attend `wait_selector` -- un sélecteur PRÉCIS qui ne peut exister que si le vrai
    contenu est arrivé, pas juste le conteneur vide -- puis retourne le HTML de
    `extract_selector`. Lève une exception explicite en cas d'échec (proxy mort, 403,
    timeout...) pour que l'appelant sache exactement pourquoi et puisse changer de proxy.
    """
    extract_selector = extract_selector or wait_selector
    context = browser.new_context(proxy={"server": proxy, "username": USERNAME, "password": PASSWORD})
    try:
        page = context.new_page()
        response = page.goto(url, timeout=timeout, wait_until="domcontentloaded")
        if response is not None and not response.ok:
            raise RuntimeError(f"HTTP {response.status} (probable blocage anti-bot)")

        try:
            page.wait_for_selector(wait_selector, timeout=timeout)
        except Exception:
            _dump_debug(page, url)
            raise
        html = page.inner_html(extract_selector)
        if not html or not html.strip():
            raise RuntimeError("sélecteur trouvé mais contenu vide")
        return html
    finally:
        context.close()


def fetch_with_retries(browser, url, proxy_list, wait_selector, extract_selector=None, start_index=0):
    """Essaie les proxies l'un après l'autre (en repartant de start_index) jusqu'à succès."""
    n = len(proxy_list)
    for attempt in range(n):
        idx = (start_index + attempt) % n  # FIX: ne peut jamais sortir des bornes de proxy_list
        proxy = proxy_list[idx]
        try:
            html = fetch_html(browser, url, proxy, wait_selector, extract_selector)
            return html, idx  # on repart de ce proxy au prochain appel, il vient de marcher
        except Exception as e:
            print(f" ------- Proxy {proxy} en échec sur {url} : {e!r} -------")  # FIX: erreur visible
            raise e
    return None, start_index

def get_property(beautifulSoupHtml, selector, multiple=False):
    if multiple:
        selections = beautifulSoupHtml.select(selector)
        if len(selections) > 0:
            element=""
            for selection in selections:
                selectionText=selection.get_text(separator="-", strip=True)
                element=f"{element}-{selectionText}"
        else:
            element="not_defined"
    else:
        selection = beautifulSoupHtml.select_one(selector)
        element=selection.get_text(separator="-", strip=True) if selection else "not_defined"
    return element

def get_job_description(beautifulSoupHtml, h2Keys):
    sections = []
    for div in beautifulSoupHtml.find_all("div"):
        h2 = div.find("h2", recursive=False)
        if h2:
            titre = h2.get_text(" ", strip=True)
            if titre in h2Keys:
                contenu = div.get_text(
                    separator=" ",
                    strip=True
                )
                sections.append(contenu)
    return "\n".join(sections) if sections else "not_defined"

def get_jobs(listing_url, maxItems=10): 
    url=listing_url
    proxy_list = initialize_proxy_list()
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
                listing_html, proxy_index = fetch_with_retries(
                    browser, url, proxy_list, wait_selector="div.content-column", start_index=proxy_index
                )
                if not listing_html:
                    print("Impossible de charger la page de listing avec les proxies disponibles.")
                    return offers
                listing_soup = BeautifulSoup(listing_html, "html.parser")
                posts = listing_soup.find_all("li", class_="post-id")
                print(f" ------- {len(posts)} offres trouvées sur la page de listing ------- ")

                for post in posts:
                    if len(offers) >= maxItems:
                        break
                    link = get_link(post)
                    if not link:
                        print(" ------- Lien introuvable pour une offre, on passe ------- ")
                        continue

                    html, proxy_index = fetch_with_retries(
                        browser, link, proxy_list,
                        wait_selector="div.contentbloc div.listWrpService.jobdetail .row h1",
                        extract_selector="div.contentbloc",
                        start_index=proxy_index,
                    )

                    if html:
                        soup=BeautifulSoup(html, "html.parser")
                        titre=get_property(beautifulSoupHtml=soup, selector="div.listWrpService.jobdetail .row h1")
                        sector=get_property(beautifulSoupHtml=soup, selector="div.listWrpService.jobdetail .row h2")
                        experience=get_property(beautifulSoupHtml=soup, selector="div.listWrpService.jobdetail .row ul.featureInfo li[title='Expérience requise']")
                        region=get_property(beautifulSoupHtml=soup, selector="div.listWrpService.jobdetail ul.featureInfo li[title='Région']")
                        formation=get_property(beautifulSoupHtml=soup, selector='div.listWrpService.jobdetail ul.featureInfo li[title="Niveau d\'étude et formation"]')
                        competencesPersonnelles=get_property(beautifulSoupHtml=soup, selector="div.listWrpService.jobdetail span.tagSkills", multiple=True)
                        contrat=get_property(beautifulSoupHtml=soup, selector="div.listWrpService.jobdetail span[title='Type de contrat']")
                        teletravail=get_property(beautifulSoupHtml=soup, selector="div.listWrpService.jobdetail span[title='Télétravail']")
                        dateLimite=get_property(beautifulSoupHtml=soup, selector="div.listWrpService.jobdetail span.newjob b")
                        description=get_job_description(beautifulSoupHtml=soup, h2Keys=["Poste :", "Profil recherché :"])

                        print(f""" ------- OK 
                            link: {link} \n
                            titre: {titre} \n
                            sector: {sector} \n
                            experience: {experience} \n
                            region: {region} \n
                            formation: {formation} \n
                            competences personelles:{competencesPersonnelles} \n
                            contrat: {contrat} \n
                            teletravail: {teletravail} \n
                            dateLimite: {dateLimite} \n
                            description: {description}
                        -------""")

                        offer={
                            "titre": titre,
                            "link": link,
                            "sector": sector,
                            "experience": experience,
                            "region": region,
                            "formation": formation,
                            "competences personelles": competencesPersonnelles,
                            "contrat": contrat,
                            "teletravail": teletravail,
                            "description": description,
                            "dateLimite": dateLimite
                        }

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