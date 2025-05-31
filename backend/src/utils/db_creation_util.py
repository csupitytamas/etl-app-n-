from sqlalchemy import text
from sqlalchemy.orm import Session
import re
import uuid

def sanitize_name(name: str) -> str:
    name = name.lower()
    name = re.sub(r'[^a-z0-9_]', '_', name)
    return name[:40]

def generate_table_name(pipeline_name: str, version: int, uid: str | None = None) -> str:
    pipeline_name = sanitize_name(pipeline_name)
    uid = uid or str(uuid.uuid4())[:8]
    return f"{pipeline_name}_v{version}_{uid}"
