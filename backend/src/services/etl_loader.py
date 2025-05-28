from sqlalchemy import Table, MetaData, insert
from sqlalchemy.orm import Session
from src.models.etl_config_model import ETLConfig
import requests

def load_to_target_table(pipeline_id: int, db: Session):
    # 1. Pipeline lekérése
    pipeline = db.query(ETLConfig).filter_by(id=pipeline_id).first()
    if not pipeline:
        raise Exception(f"Pipeline {pipeline_id} not found")

    if not pipeline.target_table_name:
        raise Exception("Target table name is missing.")

    # 2. API lekérés
    response = requests.get(pipeline.source)
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, list):
        data = [data]

    # 3. Mezők nevei a field_mappings-ből
    fields = [f["name"] for f in pipeline.field_mappings]

    # 4. Adatok előkészítése: list[dict] formában
    insert_data = []
    for row in data:
        insert_data.append({col: row.get(col) for col in fields})

    # 5. Dinamikus táblahivatkozás a MetaData segítségével
    metadata = MetaData()
    table = Table(pipeline.target_table_name, metadata, autoload_with=db.bind)

    # 6. SQLAlchemy insert (tömeges beszúrás)
    stmt = insert(table).values(insert_data)
    db.execute(stmt)
    db.commit()

    print(f"{len(insert_data)} sor betöltve a(z) {pipeline.target_table_name} táblába.")