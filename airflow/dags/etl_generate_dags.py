from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sqlalchemy as sa
import json
import requests

# PostgreSQL connection
DB_URL = "postgresql+psycopg2://postgres:admin123@host.docker.internal:5433/ETL"
engine = sa.create_engine(DB_URL)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# JSON path parser
def extract_from_path(data, path):
    keys = path.split('.')
    current = data
    for key in keys:
        if '[' in key and ']' in key:
            key_name, idx = key[:-1].split('[')
            current = current.get(key_name, [])
            idx = int(idx)
            if isinstance(current, list) and len(current) > idx:
                current = current[idx]
            else:
                return None
        else:
            if isinstance(current, dict):
                current = current.get(key, None)
            else:
                return None
        if current is None:
            return None
    return current

# Create target table based on ETL config
def create_table(pipeline_id, **kwargs):
    with engine.connect() as conn:
        query = sa.text("SELECT target_table_name, field_mappings FROM etlconfig WHERE id = :id")
        result = conn.execute(query, {"id": pipeline_id}).mappings().first()
        if not result:
            raise Exception(f"Pipeline ID {pipeline_id} not found.")

        table_name = result['target_table_name']
        field_mappings = result['field_mappings']

        if isinstance(field_mappings, str):
            field_mappings = json.loads(field_mappings)

        column_defs = []
        for col_name, props in field_mappings.items():
            col_type = props.get('type', 'TEXT')
            column_defs.append(f'"{col_name}" {col_type}')

        column_sql = ",\n  ".join(column_defs)
        create_sql = f'''
        CREATE TABLE IF NOT EXISTS "{table_name}" (
          id SERIAL PRIMARY KEY,
          {column_sql}
        );
        '''
        conn.execute(sa.text(create_sql))
        print(f"Tábla létrehozva vagy már létezett: {table_name}")

# Data extraction from API
def extract_data(pipeline_id, **kwargs):
    with engine.connect() as conn:
        query = sa.text("""
            SELECT source, field_mappings
            FROM api_schemas
            WHERE source = (SELECT source FROM etlconfig WHERE id = :id)
        """)
        result = conn.execute(query, {"id": pipeline_id}).mappings().first()

    if not result:
        raise Exception(f"API schema not found for pipeline {pipeline_id}")

    source_url = result['source']
    field_mappings = result['field_mappings']

    response = requests.get(source_url)
    if response.status_code != 200:
        raise Exception(f"API Error: {response.status_code}")

    data = response.json()
    extracted = []

    for item in data:
        record = {}
        for field in field_mappings:
            field_name = field.get('name')
            field_path = field.get('path', field_name)
            value = extract_from_path(item, field_path)
            record[field_name] = value
        extracted.append(record)

    kwargs['ti'].xcom_push(key='extracted_data', value=extracted)

# Data load to target table
def load_data(pipeline_id, **kwargs):
    data = kwargs['ti'].xcom_pull(key='extracted_data', task_ids=f"extract_data_{pipeline_id}")

    if not data:
        raise Exception("No data!")

    with engine.connect() as conn:
        query = sa.text("SELECT target_table_name FROM etlconfig WHERE id = :id")
        result = conn.execute(query, {"id": pipeline_id}).mappings().first()
        table_name = result['target_table_name']

        for row in data:
            conn.execute(sa.text(
                f'''
                INSERT INTO "{table_name}" ({', '.join(f'"{key}"' for key in row.keys())})
                VALUES ({', '.join(f':{key}' for key in row.keys())})
                '''
            ), row)
        print(f"{len(data)} Record is successfuly load  to {table_name} .")

# Pipeline select and DAG generate
with engine.connect() as conn:
    query = sa.text("SELECT * FROM etlconfig")
    pipelines = conn.execute(query).mappings().all()

for pipeline in pipelines:
    dag_id = f"etl_pipeline_{pipeline['id']}"
    schedule = pipeline['schedule']
    custom_time = pipeline.get('custom_time')

   # Schedule interval based on pipeline configuration
    if schedule == "daily":
        schedule_interval = "@daily"
    elif schedule == "hourly":
        schedule_interval = "@hourly"
    elif schedule == "custom" and custom_time:
        hour, minute = custom_time.split(':')
        schedule_interval = f"{int(minute)} {int(hour)} * * *"
    else:
        schedule_interval = None



    # DAG definition
    dag = DAG(
        dag_id=dag_id,
        description=f"DAG for {pipeline['pipeline_name']}",
        default_args=default_args,
        schedule_interval=schedule_interval,
        start_date=datetime(2025, 1, 1),
        catchup=False,
    )
    # Task definitions
    create_task = PythonOperator(
        task_id=f"create_table_{pipeline['id']}",
        python_callable=create_table,
        op_args=[pipeline['id']],
        dag=dag,
    )

    extract_task = PythonOperator(
        task_id=f"extract_data_{pipeline['id']}",
        python_callable=extract_data,
        op_args=[pipeline['id']],
        dag=dag,
    )

    load_task = PythonOperator(
        task_id=f"load_data_{pipeline['id']}",
        python_callable=load_data,
        op_args=[pipeline['id']],
        dag=dag,
    )

    # Task dependencies
    create_task >> extract_task >> load_task

    globals()[dag_id] = dag
