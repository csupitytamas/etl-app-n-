from numpy.distutils.conv_template import unique_key

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sqlalchemy as sa
import json
import requests
import pandas as pd
from transforms.data_load import load_overwrite, load_append, load_upsert
from transforms.field_mapping import field_mapping_helper, get_final_selected_columns, get_final_column_order
from transforms.transfomations import field_mapping, group_by, order_by, flatten_grouped_data
from transforms.exporter import export_data
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
    print(f"[extract_from_path] START - path: {path}")
    keys = path.split('.')
    current = data
    for i, key in enumerate(keys):
        print(f"  [Level {i}] key: {key} | current type: {type(current).__name__} | value: {str(current)[:80]}")
        if '[' in key and ']' in key:
            key_name, idx = key[:-1].split('[')
            print(f"    -> Array key: {key_name} | idx: {idx}")
            current = current.get(key_name, [])
            idx = int(idx)
            if isinstance(current, list) and len(current) > idx:
                current = current[idx]
            else:
                print("    [extract_from_path] Array index out of range or not a list, returning None.")
                return None
        else:
            if isinstance(current, dict):
                current = current.get(key, None)
                print(f"    -> Dict get: {key} -> {str(current)[:80]}")
            else:
                print("    [extract_from_path] Not a dict, returning None.")
                return None
        if current is None:
            print("    [extract_from_path] Current is None, returning None.")
            return None
    print(f"[extract_from_path] END - value: {current}")
    return current
# Create target table based on ETL config
def create_table(pipeline_id, **kwargs):
    print(f"\n=== [CREATE_TABLE] pipeline_id: {pipeline_id} ===")
    with engine.connect() as conn:
        query = sa.text("""
            SELECT target_table_name, field_mappings, selected_columns, column_order, update_mode,
                   group_by_columns, order_by_column, order_direction
            FROM etlconfig WHERE id = :id
        """)
        result = conn.execute(query, {"id": pipeline_id}).mappings().first()
        print("[CREATE_TABLE] Lekérdezett konfig:", result)
        table_name = result['target_table_name']
        field_mappings = result['field_mappings']
        selected_columns = result['selected_columns']
        column_order = result['column_order']
        update_mode = result['update_mode']
        group_by_columns = result.get('group_by_columns')
        order_by_column = result.get('order_by_column')
        order_direction = result.get('order_direction')

        # JSON decode, ha szükséges
        print("[CREATE_TABLE] JSON decode előtt:", field_mappings, selected_columns, column_order)
        if isinstance(field_mappings, str):
            field_mappings = json.loads(field_mappings)
        if isinstance(selected_columns, str):
            selected_columns = json.loads(selected_columns)
        if isinstance(column_order, str):
            column_order = json.loads(column_order)
        if isinstance(group_by_columns, str):
            group_by_columns = json.loads(group_by_columns) if group_by_columns else []

        print("[CREATE_TABLE] JSON decode után:", field_mappings, selected_columns, column_order)

        unique_cols = [col for col, props in field_mappings.items() if props.get("unique")] if field_mappings else []
        print(f"[CREATE_TABLE] Unique oszlopok: {unique_cols}")
        final_selected_columns = get_final_selected_columns(selected_columns, field_mappings)
        print(f"[CREATE_TABLE] final_selected_columns: {final_selected_columns}")
        final_column_order = get_final_column_order(column_order, field_mappings)
        print(f"[CREATE_TABLE] final_column_order: {final_column_order}")
        final_columns = field_mapping_helper(
            field_mappings,
            selected_columns=final_selected_columns,
            column_order=final_column_order
        )
        print(f"[CREATE_TABLE] FINAL COLUMNS: {final_columns}")

        # Átnevezési mapping: eredeti név -> végleges név
        col_rename_map = {}
        for orig, props in field_mappings.items():
            if props.get("delete", False):
                continue
            if props.get("rename", False) and props.get("newName"):
                col_rename_map[orig] = props["newName"]
            else:
                col_rename_map[orig] = orig
        print(f"[CREATE_TABLE] col_rename_map: {col_rename_map}")

        # group_by, order_by mapping végleges névre
        def resolve_final(col):
            mapping = field_mappings.get(col, {})
            if mapping.get("delete", False):
                return None
            if mapping.get("rename", False) and mapping.get("newName"):
                return mapping["newName"]
            return col

        mapped_group_by_columns = [resolve_final(col) for col in group_by_columns] if group_by_columns else []
        mapped_group_by_columns = [col for col in mapped_group_by_columns if col]
        mapped_order_by_column = resolve_final(order_by_column) if order_by_column else None

        print(f"[CREATE_TABLE] mapped_group_by_columns: {mapped_group_by_columns}")
        print(f"[CREATE_TABLE] mapped_order_by_column: {mapped_order_by_column}")

        # --- Tábla létrehozás ---
        column_defs = []
        for col in final_columns:
            props = next((p for k, p in field_mappings.items()
                          if (p.get("rename") and p.get("newName") == col) or k == col), {})
            col_type = props.get('type', 'TEXT')
            col_def = f'"{col}" {col_type}'
            if update_mode == "upsert" and props.get('unique'):
                col_def += " UNIQUE"
            column_defs.append(col_def)
        print(f"[CREATE_TABLE] column_defs: {column_defs}")

        if not column_defs:
            print("[CREATE_TABLE] ERROR: Nincs egyetlen oszlop sem!")
            raise Exception("A tábla nem hozható létre, mert nincs egyetlen oszlop sem a field mapping alapján!")

        column_sql = ",\n  ".join(column_defs)
        create_sql = f'''
        CREATE TABLE IF NOT EXISTS "{table_name}" (
          id SERIAL PRIMARY KEY{',' if column_sql else ''}
          {column_sql}
        );
        '''
        print("[CREATE_TABLE] CREATE SQL:\n", create_sql)
        conn.execute(sa.text(create_sql))
        print(f"[CREATE_TABLE] Tábla létrehozva vagy már létezett: {table_name}")

        # XCom push – minden szerkezet infó, amit a transform/load taskoknak tudni kell!
        ti = kwargs['ti']
        print("[CREATE_TABLE] XCom push: final_columns, col_rename_map, group_by_columns, order_by_column, order_direction, unique_cols")
        ti.xcom_push(key='final_columns', value=final_columns)
        ti.xcom_push(key='col_rename_map', value=col_rename_map)
        ti.xcom_push(key='group_by_columns', value=mapped_group_by_columns)
        ti.xcom_push(key='order_by_column', value=mapped_order_by_column)
        ti.xcom_push(key='order_direction', value=order_direction)
        ti.xcom_push(key='unique_cols', value=unique_cols)

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
    print(f"\n=== [TRANSFORM_DATA] pipeline_id: {pipeline_id} ===")
    ti = kwargs['ti']
    data = ti.xcom_pull(key='extracted_data', task_ids=f"extract_data_{pipeline_id}")
    print(f"[TRANSFORM_DATA] Extracted data (sample): {data[:2]}")

    if not data:
        print("[TRANSFORM_DATA] ERROR: Nincs adat az extractból!")
        raise Exception("Nincs adat az extractból!")

    final_columns = ti.xcom_pull(key='final_columns', task_ids=f"create_table_{pipeline_id}")
    col_rename_map = ti.xcom_pull(key='col_rename_map', task_ids=f"create_table_{pipeline_id}")
    group_by_columns = ti.xcom_pull(key='group_by_columns', task_ids=f"create_table_{pipeline_id}")
    order_by_column = ti.xcom_pull(key='order_by_column', task_ids=f"create_table_{pipeline_id}")
    order_direction = ti.xcom_pull(key='order_direction', task_ids=f"create_table_{pipeline_id}")

    print(f"[TRANSFORM_DATA] final_columns: {final_columns}")
    print(f"[TRANSFORM_DATA] col_rename_map: {col_rename_map}")
    print(f"[TRANSFORM_DATA] group_by_columns: {group_by_columns}")
    print(f"[TRANSFORM_DATA] order_by_column: {order_by_column}, order_direction: {order_direction}")

    if not final_columns or not col_rename_map:
        print("[TRANSFORM_DATA] ERROR: Hiányzik a végleges szerkezet vagy mapping!")
        raise Exception("Nincs végleges szerkezet vagy mapping! Ellenőrizd a create_table task XCom push-okat!")

    # 1. Field mapping (átnevezés, törlés, sorrend)
    transformed = field_mapping(data, col_rename_map, final_columns)
    print(f"[TRANSFORM_DATA] Transformed (mapped) data (sample): {transformed[:2]}")
    ti.xcom_push(key='transformed_data', value=transformed)

    # 2. Rendezés
    if order_by_column:
        print(f"[TRANSFORM_DATA] Ordering by: {order_by_column} ({order_direction})")
        ordered = order_by(
            transformed,
            [order_by_column],
            order_direction
        )
    else:
        print("[TRANSFORM_DATA] No ordering applied.")
        ordered = transformed
    print(f"[TRANSFORM_DATA] Ordered data (sample): {ordered[:2]}")
    ti.xcom_push(key='ordered_data', value=ordered)

    # 3. Csoportosítás (group by)
    if group_by_columns:
        print(f"[TRANSFORM_DATA] Grouping by: {group_by_columns}")
        grouped = group_by(ordered, group_by_columns)
        ti.xcom_push(key='group_by_data', value=grouped)
        flattened = flatten_grouped_data(grouped)
        print(f"[TRANSFORM_DATA] Flattened grouped data (sample): {flattened[:2]}")
        ti.xcom_push(key='final_data', value=flattened)
    else:
        print("[TRANSFORM_DATA] No group by applied, final data is ordered data.")
        ti.xcom_push(key='final_data', value=ordered)
# Data load to target table
def load_data(pipeline_id, **kwargs):
    print(f"\n=== [LOAD_DATA] pipeline_id: {pipeline_id} ===")
    ti = kwargs['ti']
    data = ti.xcom_pull(key='final_data', task_ids=f"transform_data_{pipeline_id}")
    print(f"[LOAD_DATA] final_data (sample): {data[:2]}")

    if not data:
        print("[LOAD_DATA] ERROR: No data to load!")
        raise Exception("No data to load!")

    final_columns = ti.xcom_pull(key='final_columns', task_ids=f"create_table_{pipeline_id}")
    print(f"[LOAD_DATA] final_columns: {final_columns}")
    if not final_columns:
        print("[LOAD_DATA] ERROR: Nincs final_columns XCom-ban! Ellenőrizd a create_table-t.")
        raise Exception("Nincs final_columns XCom-ban! Ellenőrizd a create_table-t.")

    allowed_columns = set(final_columns)
    filtered_data = [{k: v for k, v in row.items() if k in allowed_columns} for row in data]
    print(f"[LOAD_DATA] filtered_data (sample): {filtered_data[:2]}")

    with engine.connect() as conn:
        query = sa.text("SELECT target_table_name, update_mode, file_format, save_option FROM etlconfig WHERE id = :id")
        result = conn.execute(query, {"id": pipeline_id}).mappings().first()
        print(f"[LOAD_DATA] etlconfig row: {result}")
        table_name = result['target_table_name']
        update_mode = result['update_mode']
        file_format = result['file_format']
        save_option = result['save_option']
        unique_cols = ti.xcom_pull(key='unique_cols', task_ids=f"create_table_{pipeline_id}")
        print(f"[LOAD_DATA] unique_cols: {unique_cols}")

        if update_mode == "overwrite":
            print(f"[LOAD_DATA] Mode: overwrite. Table: {table_name}")
            load_overwrite(table_name, filtered_data, conn)
        elif update_mode == "append":
            print(f"[LOAD_DATA] Mode: append. Table: {table_name}")
            load_append(table_name, filtered_data, conn)
        elif update_mode == "upsert":
            print(f"[LOAD_DATA] Mode: upsert. Table: {table_name}")
            if not unique_cols:
                print("[LOAD_DATA] ERROR: Upsert módban nincs unique mező!")
                raise Exception("Upsert módban legalább egy oszlopnál kötelező a unique mező!")
            load_upsert(table_name, filtered_data, conn, unique_cols=unique_cols)
        else:
            print(f"[LOAD_DATA] ERROR: Ismeretlen update_mode: {update_mode}")

        if save_option == "createfile":
            print(f"[LOAD_DATA] Export file, format: {file_format}")
            df = pd.DataFrame(filtered_data)
            export_data(df, table_name, file_format)
            print("Fájl exportálva:", table_name, file_format)

    print(f"[LOAD_DATA] {len(filtered_data)} rekord került betöltésre a(z) {table_name} táblába ({update_mode} móddal).")

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
