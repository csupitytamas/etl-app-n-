from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sqlalchemy as sa
import json
import requests

from transforms.data_load import load_overwrite, load_append, load_upsert
from transforms.field_mapping import field_mapping_helper
from transforms.transfomations import field_mapping, group_by, order_by, flatten_grouped_data

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
        query = sa.text("""
            SELECT target_table_name, field_mappings, selected_columns, column_order, update_mode
            FROM etlconfig WHERE id = :id
        """)
        result = conn.execute(query, {"id": pipeline_id}).mappings().first()
        table_name = result['target_table_name']
        field_mappings = result['field_mappings']
        selected_columns = result['selected_columns']
        column_order = result['column_order']
        update_mode = result['update_mode']

        # JSON decode, ha szükséges
        if isinstance(field_mappings, str):
            field_mappings = json.loads(field_mappings)
        if isinstance(selected_columns, str):
            selected_columns = json.loads(selected_columns)
        if isinstance(column_order, str):
            column_order = json.loads(column_order)

        # Segédfüggvény meghívása!
        final_columns = field_mapping_helper(
            field_mappings,
            selected_columns=selected_columns,
            column_order=column_order
        )

        column_defs = []
        for col in final_columns:
            props = next((p for k, p in field_mappings.items()
                          if (p.get("rename") and p.get("newName") == col) or k == col), {})
            col_type = props.get('type', 'TEXT')
            col_def = f'"{col}" {col_type}'
            # Csak upsert esetén legyen UNIQUE
            if update_mode == "upsert" and props.get('unique'):
                col_def += " UNIQUE"
            column_defs.append(col_def)

        if not column_defs:
            raise Exception("A tábla nem hozható létre, mert nincs egyetlen oszlop sem a field mapping alapján!")

        column_sql = ",\n  ".join(column_defs)
        create_sql = f'''
        CREATE TABLE IF NOT EXISTS "{table_name}" (
          id SERIAL PRIMARY KEY{',' if column_sql else ''}
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

def transform_data(pipeline_id, **kwargs):
    ti = kwargs['ti']
    data = ti.xcom_pull(key='extracted_data', task_ids=f"extract_data_{pipeline_id}")

    if not data:
        raise Exception("Nincs adat az extractból!")

    with engine.connect() as conn:
        query = sa.text("SELECT field_mappings, group_by_columns, order_by_column, order_direction FROM etlconfig WHERE id = :id")
        result = conn.execute(query, {"id": pipeline_id}).mappings().first()
        field_mappings = result['field_mappings']
        group_by_columns = result['group_by_columns']
        order_by_column = result['order_by_column']
        order_direction = result['order_direction']

        if isinstance(field_mappings, str):
            field_mappings = json.loads(field_mappings)
        if isinstance(group_by_columns, str):
            group_by_columns = json.loads(group_by_columns)

    # 1. Transzformáció
    transformed = field_mapping(data, field_mappings)
    ti.xcom_push(key='transformed_data', value=transformed)

    # 2. Rendezés
    if order_by_column:
        ordered = order_by(transformed, [order_by_column], order_direction)
    else:
        ordered = transformed
    ti.xcom_push(key='ordered_data', value=ordered)

    # 3. Csoportosítás
    if group_by_columns:
        grouped = group_by(ordered, group_by_columns)
        ti.xcom_push(key='group_by_data', value=grouped)
        flattened = flatten_grouped_data(grouped)
        ti.xcom_push(key='final_data', value=flattened)
    else:
        ti.xcom_push(key='final_data', value=ordered)

# Data load to target table
def load_data(pipeline_id, **kwargs):
    ti = kwargs['ti']
    data = ti.xcom_pull(key='final_data', task_ids=f"transform_data_{pipeline_id}")

    if not data:
        raise Exception("No data to load!")

    with engine.connect() as conn:
        query = sa.text("SELECT target_table_name, update_mode, field_mappings FROM etlconfig WHERE id = :id")
        result = conn.execute(query, {"id": pipeline_id}).mappings().first()
        table_name = result['target_table_name']
        update_mode = result['update_mode']
        field_mappings = result['field_mappings']


        if isinstance(field_mappings, str):
            field_mappings = json.loads(field_mappings)

        unique_cols = [col for col, props in field_mappings.items() if props.get("unique")]


        if update_mode == "overwrite":
            load_overwrite(table_name, data, conn)
        elif update_mode == "append":
            load_append(table_name, data, conn)
        elif update_mode == "upsert":
            if not unique_cols:
                raise Exception("Upsert módban legalább egy oszlopnál kötelező a unique mező!")
            load_upsert(table_name, data, conn, unique_cols=unique_cols)

    print(f"{len(data)} record került betöltésre a(z) {table_name} táblába ({update_mode} móddal).")

# Pipeline select and DAG generate
with engine.connect() as conn:
    query = sa.text("SELECT * FROM etlconfig")
    pipelines = conn.execute(query).mappings().all()

for pipeline in pipelines:
    dag_id = pipeline['dag_id']
    print(f"[ETL DAG CREATE] dag_id: {dag_id}")
    schedule = pipeline['schedule']
    custom_time = pipeline.get('custom_time')

   # Schedule interval based on pipeline configuration
    if schedule == "daily":
        schedule_interval = "@daily"
    elif schedule == "hourly":
        schedule_interval = "@hourly"
    elif schedule == "weekly":
        schedule_interval = "@weekly"
    elif schedule == "monthly":
        schedule_interval == "@monthly"
    elif schedule == "yearly":
        schedule_interval = "@yearly"
    elif schedule == "once":
        schedule_interval = "@once"
    elif schedule == "never":
        schedule_interval = None
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
        is_paused_upon_creation=False
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

    transform_task = PythonOperator(
        task_id=f"transform_data_{pipeline['id']}",
        python_callable=transform_data,
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
    create_task >> extract_task >> transform_task >> load_task

    globals()[dag_id] = dag
