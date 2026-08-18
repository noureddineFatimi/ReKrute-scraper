import os
import logging
from dotenv import load_dotenv

load_dotenv()
#wa9t twil dyel traitement,  ki b9a it3awd kolla mra ?

PROXY_USERNAME = os.getenv("PROXY_USERNAME")
PASSWORD = os.getenv("PASSWORD")

if PROXY_USERNAME is None or PASSWORD is None:
    logging.error(
        "Proxy username or password is missing in the .env file "
        "or in the environment variables."
    )
    raise RuntimeError("Proxy username or password is missing")