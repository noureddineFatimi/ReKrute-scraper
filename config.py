import os
from dotenv import load_dotenv

load_dotenv() 

PROXY_USERNAME = os.getenv("PROXY_USERNAME")
PASSWORD = os.getenv("PASSWORD")