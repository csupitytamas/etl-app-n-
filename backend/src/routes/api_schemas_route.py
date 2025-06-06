from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.db.connection import get_db
from src.models import APISchema
from src.schemas.api_schemas_schema import  SourceAlias,  SourceRequest
import json
from src.services.etl_loader import load_to_target_table

router = APIRouter()

@router.post("/load/{pipeline_id}")

def run_pipeline_load(pipeline_id: int, db: Session = Depends(get_db)):
    try:
        load_to_target_table(pipeline_id, db)
        return {"message": "Data loaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/available-sources", response_model=List[SourceAlias])
def get_available_sources(db: Session = Depends(get_db)):
    sources = db.query(APISchema.source, APISchema.alias, APISchema.description).all()
    return [{"source": row[0], "alias": row[1], "description": row[2]} for row in sources]




@router.post("/load-schema")
def load_schema(req: SourceRequest, db: Session = Depends(get_db)):
    normalized_source = req.source.strip().rstrip('/')
    schema = db.query(APISchema).filter(APISchema.source == normalized_source).first()

    if not schema:
        raise HTTPException(status_code=404, detail="Schema not found.")

    if isinstance(schema.field_mappings, str):
        try:
            field_mappings = json.loads(schema.field_mappings)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="field_mappings is not valid JSON string.")
    else:
        field_mappings = schema.field_mappings

    return {
        "field_mappings": field_mappings,
        "column_order": [f["name"] for f in field_mappings]
    }

