from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import sqlalchemy as sa
import logging


def print_etlconfigs():
    engine = sa.create_engine("postgresql+psycopg2://postgres:admin123@host.docker.internal:5433/ETL")
    
    with engine.connect() as conn:
        result = conn.execute(sa.text("SELECT id, pipeline_name FROM etlconfig"))
        for row in result:
            print(f" Pipeline ID: {row.id}, Name: {row.pipeline_name}")
    logging.getLogger().setLevel(logging.ERROR)

with DAG(
    dag_id="etl_debug_dag",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False
) as dag:
    t1 = PythonOperator(
        task_id="print_etlconfigs",
        python_callable=print_etlconfigs
    )
