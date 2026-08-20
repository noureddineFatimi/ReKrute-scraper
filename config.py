import os
import logging
from dotenv import load_dotenv

load_dotenv()

PROXY_USERNAME = os.getenv("PROXY_USERNAME")
PASSWORD = os.getenv("PASSWORD")
DATABASE_URL=os.getenv("DATABASE_URL")
PENDING = "pending" 
DONE = "done"
FAILED = "failed"

if PROXY_USERNAME is None or PASSWORD is None:
    logging.error(
        "Proxy username or password is missing in the .env file "
        "or in the environment variables."
    )
    raise RuntimeError("Proxy username or password is missing")

if DATABASE_URL is None :
    logging.error(
        "database url is missing"
    )
    raise RuntimeError("database url is missing")

