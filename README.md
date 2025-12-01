


# Crypto Feature Store

A robust, containerized data engineering project that creates a feature store for cryptocurrency data. It automates the ingestion of raw price data, transforms it into machine learning features (like rolling means and volatility), and serves the data via a high-performance REST API.

## 🚀 Key Features

* **Automated Ingestion**: Fetches historical and real-time Bitcoin prices from the CoinGecko API.
* **Data Transformation**: Calculates financial features (returns, rolling means, standard deviations) using **Polars** for high performance.
* **Data Quality**: Validates all feature data using **Pandera** schemas before storage.
* **Orchestration**: Uses **Apache Airflow** to schedule and monitor data pipelines.
* **Serving Layer**: Exposes data via a **FastAPI** application with automatic Swagger documentation.
* **Containerization**: Fully Dockerized environment including Airflow, PostgreSQL, and the API.

## 🛠️ Tech Stack

* **Language**: Python 3.8+
* **Orchestration**: Apache Airflow
* **Web Framework**: FastAPI & Uvicorn
* **Database**: PostgreSQL 16
* **Data Processing**: Polars, Pandas, SQLAlchemy
* **Validation**: Pandera
* **Infrastructure**: Docker & Docker Compose


## ⚡Getting Started
1. Build and Run
Start the entire stack with a single command. This will build the Docker images and start Airflow, Postgres, and the API.

```bash
docker-compose up --build
```
Note: Wait for the logs to settle. The first run may take a few minutes to initialize the Airflow database and install dependencies.

## 🖥️ Usage Guide
Accessing the Interfaces
Airflow UI: http://localhost:8080

Credentials: admin / admin

API Documentation (Swagger UI): http://localhost:8000/docs

API Health Check: http://localhost:8000/health

Running the Pipeline
Go to the Airflow UI at http://localhost:8080.

Locate the DAG named crypto_feature_store_pipeline.

Toggle the Pause/Unpause switch to ON.

Click the Trigger DAG button (▶️) to run the pipeline manually.

Watch the tasks ingest_btc and build_features turn green (Success).



## 📂 Project Structure

```text
crypto-feature-store/
├── dags/
│   └── crypto_feature_store_dag.py    # Airflow DAG definition
├── src/
│   └── crypto_feature_store/
│       ├── api/                       # FastAPI application
│       ├── db/                        # Database session & engine
│       ├── ingestion/                 # Logic to fetch data from CoinGecko
│       ├── models/                    # SQLAlchemy & Pydantic models
│       └── pipelines/                 # Transformation logic (Polars/Pandera)
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

