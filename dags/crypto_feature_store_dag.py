from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

# Import your actual pipeline functions
# NOTE: These imports work because we set PYTHONPATH=/opt/airflow/src in docker-compose
from crypto_feature_store.ingestion.prices_ingestor import run_ingestion
from crypto_feature_store.pipelines.transform_prices import run_transform

default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    dag_id="crypto_feature_store_pipeline",
    default_args=default_args,
    description="Ingest BTC prices and calculate features",
    schedule_interval="*/15 * * * *",  # Run every 15 minutes
    start_date=datetime(2025, 11, 26),
    catchup=False,
    tags=["crypto", "feature_store"],
) as dag:

    # Task 1: Fetch prices from CoinGecko and save to Postgres (price_bars)
    ingest_task = PythonOperator(
        task_id="ingest_btc",
        python_callable=run_ingestion,
    )

    # Task 2: Read price_bars, calculate features, and save to price_features
    transform_task = PythonOperator(
        task_id="build_features",
        python_callable=run_transform,
    )

    # Set dependency: Transform runs ONLY after Ingestion succeeds
    ingest_task >> transform_task