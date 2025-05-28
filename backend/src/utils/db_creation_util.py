from sqlalchemy import text
from sqlalchemy.orm import Session
import re
import uuid

def sanitize_name(name: str) -> str:
    """Távolítson el minden nem alfanumerikus vagy aláhúzás karaktert, és kisbetűsre vált."""
    name = name.lower()
    name = re.sub(r'[^a-z0-9_]', '_', name)
    return name[:40]

def generate_table_name(pipeline_name: str, version: int, uid: str | None = None) -> str:
    """Létrehoz egy egyedi, verziózott tábla nevet."""
    pipeline_name = sanitize_name(pipeline_name)
    uid = uid or str(uuid.uuid4())[:8]  # rövidített UUID
    return f"{pipeline_name}_v{version}_{uid}"

def create_table_from_schema(table_name: str, field_mappings: list[dict], db: Session):
    column_defs = [f'"{field["name"]}" {field["type"]}' for field in field_mappings]
    column_sql = ",\n  ".join(column_defs)
    sql = f'''
    CREATE TABLE IF NOT EXISTS "{table_name}" (
      id SERIAL PRIMARY KEY,
      {column_sql}
    );
    '''
    db.execute(text(sql))
    db.commit()