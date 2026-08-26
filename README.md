# Rekrute Scraper

This project is a web scraping solution designed to extract job offer data from the Moroccan job board, `rekrute.com`. It is built with a FastAPI backend that provides an API to manage and retrieve scraping tasks. The scraper itself uses Playwright for browser automation and BeautifulSoup for HTML parsing, and it includes features like proxy rotation and robust error handling.

## Features

-   **Asynchronous Scraping Jobs**: Initiate scraping tasks via an API endpoint. The scraping runs in a background thread, allowing the API to remain responsive.
-   **Robust Scraping Engine**: Utilizes Playwright to navigate JavaScript-heavy pages and BeautifulSoup for efficient HTML parsing.
-   **Proxy Rotation**: Cycles through a user-provided list of proxies to avoid IP bans and handle failed requests.
-   **Data Persistence**: Scraped job offers are saved to a SQL database using SQLModel.
-   **Simple API**: Provides clear endpoints to start a scraping job and to check its status and retrieve the collected data.
-   **Error Handling**: Captures and logs errors during the scraping process, updating the job status accordingly.

## Project Structure

The repository is organized into several modules:

-   `main.py`: The entry point for the FastAPI application.
-   `config.py`: Manages configuration by loading environment variables.
-   `database.py`: Configures the database connection and session management with SQLModel.
-   `/scraper`: Contains the core scraping logic.
    -   `rekrute.py`: Main scraper function that orchestrates the process of fetching and parsing job offers.
    -   `utils.py`: Helper functions for proxy management, fetching pages with retries, and parsing HTML content.
-   `/services`: Contains the business logic.
    -   `search_service.py`: Handles the creation of search jobs, launching background scraping threads, and retrieving data.
-   `/routers`: Defines the API endpoints.
    -   `searches.py`: Implements the `/searches` routes for creating and retrieving scraping jobs.
-   `/models`: Defines the data structures.
    -   `database.py`: SQLModel table definitions for `SearchJob` and `Offer`.
    -   `schemas.py`: Pydantic models for API request validation and response serialization.

## API Endpoints

### Start a New Scraping Job

Initiates a new scraping job for a given `rekrute.com` URL. The job is processed in the background.

-   **Endpoint**: `POST /searches`
-   **Request Body**:
    ```json
    {
      "url": "https://www.rekrute.com/offres.html?s=3&p=1&o=1",
      "maxItems": 50
    }
    ```
-   **Success Response** (`200 OK`):
    ```json
    {
      "search_id": 1,
      "status": "pending"
    }
    ```

### Retrieve Scraping Job Results

Fetches the status and results of a specific scraping job by its ID.

-   **Endpoint**: `GET /searches/{search_id}`
-   **Success Response** (`200 OK`):
    ```json
    {
        "search_id": 1,
        "status": "done",
        "count": 50,
        "offers": [
            {
                "id": 1,
                "titre": "Développeur Full-Stack",
                "link": "https://www.rekrute.com/...",
                "sector": "Informatique - Développement",
                "experience": "1 à 3 ans",
                "region": "Casablanca",
                "formation": "Bac +5",
                "competencesPersonnelles": "Agilité - Rigueur",
                "contrat": "CDI",
                "teletravail": "not_defined",
                "description": "Poste : ... Profil recherché : ...",
                "dateLimite": "30/08/2024"
            }
        ],
        "error": null
    }
    ```

## Installation and Usage

Follow these steps to set up and run the project locally.

### 1. Prerequisites

-   Python 3.8+
-   A running SQL database (e.g., PostgreSQL, SQLite)

### 2. Clone the Repository

```bash
git clone https://github.com/noureddinefatimi/rekrute-scraper.git
cd rekrute-scraper
```

### 3. Install Dependencies

It is recommended to use a virtual environment.

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

pip install -r requirements.txt
```

### 4. Install Playwright Browsers

The scraper requires browser binaries for Playwright.

```bash
playwright install
```

### 5. Configure Environment Variables

Create a `.env` file in the root directory and add the necessary configuration.

```dotenv
# .env

# Example for SQLite
DATABASE_URL="sqlite:///database.db"

# Credentials for your proxy service
PROXY_USERNAME="your_proxy_username"
PASSWORD="your_proxy_password"
```

### 6. Create Proxy List

Create a file named `proxy-list.txt` in the root directory. Add your proxies, one per line, in the format `host:port`. You can also include `DIRECT` to make a direct connection without a proxy.

```
# proxy-list.txt
192.168.1.1:8080
192.168.1.2:8080
DIRECT
```

### 7. Run the Application

Use `uvicorn` to start the FastAPI server.

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`, and you can access the interactive documentation at `http://127.0.0.1:8000/docs`.
