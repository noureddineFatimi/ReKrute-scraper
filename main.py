from fastapi import FastAPI
from routers import offer, search
import uvicorn
from database import create_db_and_tables

create_db_and_tables()

app = FastAPI(title="Scraping Management API")

app.include_router(offer.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)