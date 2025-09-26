# 🌍 WFP Food Prices API

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)  
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com/)  
[![Postgres](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://www.postgresql.org/)  
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)


A simple project to explore and serve **World Food Programme (WFP)** food price data.  
The goal is to provide a clean API for querying markets, commodities, and prices, with options to filter by market, commodity, and date ranges.

---

## ✨ Features
- Import raw **WFP CSV food price data** into PostgreSQL  
- REST API with endpoints for:
  - `/markets` → list of markets  
  - `/commodities` → list of food commodities  
  - `/prices` → historical prices with filters (market, commodity, date range)  
  - `/latest-prices` → snapshot of the most recent prices 
  - `/markets/{market_id}` → filter by market
  - `/commodities/{commodity_id}` → filter by commodity
- Built with **FastAPI**, **SQLAlchemy**, and **PostgreSQL**  
- Containerized PostgreSQL setup with **Docker**  

---

## ⚡ Quickstart

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/wfp-api.git
cd wfp-api
```

### 2. Create a virtual environment
The repo has a Makefile that creates a virtual environment and installs the dependencies for the project. Run the command below:
```bash
make
```

### 3. Activate virtual environment
The command below will tell you which command to run to activate it:
```bash
make activate
```

### 4. Start PostgreSQL (Docker)
```bash
docker-compose up -d
```
This runs a local Postgres instance with the database `wfp_db`. Username and password default values are defined in the docker-compose.yml at the root of the project, and it is highly encouraged to change them before running the command above.
- **Make sure that a .env file is created at the root of the project with the URL for the database. Using the default values in the yaml, the contents of the .env file should look like this:** `DATABASE_URL=postgresql://wfp_user:wfp_pass@localhost:5432/wfp_db`

### 5. Load CSV data
The original .csv file was obtained through [HDX](https://data.humdata.org/dataset/global-wfp-food-prices), which updates it every month. If you want to work with the latest data, please replace the file under `data/` and update `CSV_PATH` value in `scripts/load_csv.py`.
When ready, run the command below:
```bash
python -m scripts.load_csv
```

### 6. Run the API
```bash
uvicorn app.main:app --reload
```
API will be available at:
👉http://localhost:8000


---

## 🛠️ Example endpoints
### - List markets:
```bash
GET /markets

```
### - Filter prices by market + date range:
```bash
GET /prices?market_id=3690&start_date=2025-01-01&end_date=2025-01-31

```
### - Latest prices snapshot:
```bash
GET /latest-prices
```

Interactive API docs can be found at [http://localhost:8000/docs](http://localhost:8000/docs).