from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sqlalchemy as sa
import json
import requests
import time

from transforms.generate_columns_from_field_mappings import generate_columns_from_field_mappings
from src.database.connection import engine
from transforms.etl_transforms import transform_data


# --- ADATBÁZIS KAPCSOLAT ---
# PostgreSQL connection string - hogyan éri el a program az adatbázist
DB_URL = "postgresql+psycopg2://postgres:admin123@host.docker.internal:5433/ETL"

# Létrehozzuk az SQLAlchemy engine-t az adatbázis eléréséhez
engine = sa.create_engine(DB_URL)

# --- AIRFLOW DEFAULT ARGUMENTUMOK ---
# Minden DAG ezekkel az alapbeállításokkal indul, hacsak felül nem írjuk őket
default_args = {
    'owner': 'airflow',  # Ki a felelős a DAG-ért
    'depends_on_past': False,  # Nem függ előző futások sikerétől
    'retries': 3,  # Hányszor próbálja újra ha hibázik
    'retry_delay': timedelta(minutes=5),  # Milyen időközzel próbálja újra
}


# --- HELPER FÜGGVÉNYEK ---

def extract_from_path(data, path):
    """
    JSON adatban való keresés, megadott 'path' útvonal mentén.
    Példa: 'user.address.city' --> data['user']['address']['city']
    """
    keys = path.split('.')
    current = data
    for key in keys:
        if '[' in key and ']' in key:  # Listák kezelése pl: data['items'][0]
            key_name, idx = key[:-1].split('[')
            current = current.get(key_name, [])
            idx = int(idx)
            if isinstance(current, list) and len(current) > idx:
                current = current[idx]
            else:
                return None
        else:  # Dict kezelése
            if isinstance(current, dict):
                current = current.get(key, None)
            else:
                return None
        if current is None:
            return None
    return current


def create_table(pipeline_id, **kwargs):
    """
    Céltábla létrehozása az adatbázisban egy pipeline ID alapján.
    Ha a tábla már létezik, először töröljük majd újra létrehozzuk (fejlesztői módban!).
    """
    with engine.connect() as conn:
        # Lekérdezzük az ETL pipeline konfigurációt az adatbázisból
        query = sa.text("SELECT target_table_name, field_mappings FROM etlconfig WHERE id = :id")
        result = conn.execute(query, {"id": pipeline_id}).mappings().first()
        if not result:
            raise Exception(f"Pipeline ID {pipeline_id} not found.")

        table_name = result['target_table_name']
        field_mappings = result['field_mappings']

        # Ha a field_mappings JSON string, alakítsuk át dict-é
        if isinstance(field_mappings, str):
            field_mappings = json.loads(field_mappings)

        # Generáljuk az oszlopneveket field_mappings alapján
        column_names = generate_columns_from_field_mappings(field_mappings)

        column_defs = []
        for col_name in column_names:
            col_type = 'TEXT'  # Alapértelmezett adattípus (később bővíthető!)
            column_defs.append(f'"{col_name}" {col_type}')

        # SQL parancs összerakása
        column_sql = ",\n  ".join(column_defs)

        # --- FIGYELEM: fejlesztési célra, törli a meglévő táblát! ---
        drop_sql = f'DROP TABLE IF EXISTS "{table_name}" CASCADE;'
        create_sql = f'''
        CREATE TABLE "{table_name}" (
          id SERIAL PRIMARY KEY,
          {column_sql}
        );
        '''
        # Tábla törlése és újralétrehozása
        conn.execute(sa.text(drop_sql))
        conn.execute(sa.text(create_sql))
        print(f"Tábla újralétrehozva: {table_name}")


def extract_data(pipeline_id, **kwargs):
    """
    API hívás: adatokat kér le egy külső forrásból és eltárolja XCom-ban.
    """
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

    # 3-szori próbálkozás ha hiba van
    for attempt in range(3):
        try:
            response = requests.get(source_url)
            if response.status_code == 200:
                break  # Siker
            else:
                print(f"Attempt {attempt+1}: API error {response.status_code}")
                time.sleep(5)
        except Exception as e:
            print(f"Attempt {attempt+1}: Exception {str(e)}")
            time.sleep(5)
    else:
        raise Exception(f"API unreachable after 3 attempts: {source_url}")

    # API válasz JSON formátumban
    data = response.json()
    extracted = []

    # Adatok kigyűjtése field mapping alapján
    for item in data:
        record = {}
        for field in field_mappings:
            field_name = field.get('name')
            field_path = field.get('path', field_name)
            value = extract_from_path(item, field_path)
            record[field_name] = value
        extracted.append(record)

    # Mentés XCom-ba, hogy más task-ok (pl. transform) is elérjék
    kwargs['ti'].xcom_push(key='extracted_data', value=extracted)


def load_data(pipeline_id, **kwargs):
    """
    Transformált adatok betöltése a céltáblába.
    """
    # Lekérjük az átalakított adatokat XCom-ból
    data = kwargs['ti'].xcom_pull(key='transformed_data', task_ids=f"transform_data_{pipeline_id}")

    if not data:
        raise Exception("No transformed data!")

    valid_columns = list(data[0].keys()) if data else []

    with engine.connect() as conn:
        query = sa.text("SELECT target_table_name FROM etlconfig WHERE id = :id")
        result = conn.execute(query, {"id": pipeline_id}).mappings().first()
        table_name = result['target_table_name']

        # Soronkénti adatbeszúrás
        for row in data:
            filtered_row = {key: value for key, value in row.items() if key in valid_columns}
            if not filtered_row:
                continue  # Ha üres, skip

            # Dinamikus SQL beszúrás
            conn.execute(sa.text(
                f'''
                INSERT INTO "{table_name}" ({', '.join(f'"{key}"' for key in filtered_row.keys())})
                VALUES ({', '.join(f':{key}' for key in filtered_row.keys())})
                '''
            ), filtered_row)

        print(f"{len(data)} records successfully loaded to {table_name}.")


# --- DINAMIKUS DAG GENERÁLÁS ---

# Az összes pipeline-t betöltjük az adatbázisból
with engine.connect() as conn:
    query = sa.text("""
        SELECT etl.*, s.current_status
        FROM etlconfig etl
        JOIN status s ON etl.id = s.etlconfig_id
    """)
    pipelines = conn.execute(query).mappings().all()

# Minden pipeline-ból egy külön DAG-ot hozunk létre
for pipeline in pipelines:
    dag_id = pipeline['dag_id']
    print(f"[ETL DAG CREATE] dag_id: {dag_id}")
    schedule = pipeline['schedule']
    custom_time = pipeline.get('custom_time')

    # Állapot alapján indítás
    is_paused = pipeline['current_status'] == 'archived'

    # Ütemezési logika
    if schedule == "daily":
        schedule_interval = "@daily"
    elif schedule == "hourly":
        schedule_interval = "@hourly"
    elif schedule == "custom" and custom_time:
        hour, minute = custom_time.split(':')
        schedule_interval = f"{int(minute)} {int(hour)} * * *"
    else:
        schedule_interval = None  # Nem ütemezett

    # Létrehozzuk a DAG-ot
    dag = DAG(
        dag_id=dag_id,
        description=f"DAG for {pipeline['pipeline_name']}",
        default_args=default_args,
        schedule_interval=schedule_interval,
        start_date=datetime(2025, 1, 1),  # Bármilyen régi dátum, catchup kikapcsolva
        catchup=False,
        is_paused_upon_creation=is_paused
    )

    # Task-ok definíciója
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
        op_kwargs={'engine': engine},
        dag=dag,
    )

    load_task = PythonOperator(
        task_id=f"load_data_{pipeline['id']}",
        python_callable=load_data,
        op_args=[pipeline['id']],
        dag=dag,
    )

    # Meghatározzuk a task sorrendet (dependency graph)
    create_task >> extract_task >> transform_task >> load_task

    # Dinamikusan hozzáadjuk a DAG-ot a globals-hoz, hogy Airflow felismerje
    globals()[dag_id] = dag