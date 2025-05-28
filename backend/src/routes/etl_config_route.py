from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from src.schemas.etl_config_schema import  ETLConfigBase, ETLConfigUpdate, ETLConfigResponse
from src.db.connection import get_db
from src.models.etl_config_model import ETLConfig
from src.models.api_schemas_model import APISchema
from src.utils.db_creation_util import generate_table_name, create_table_from_schema
from src.services.etl_loader import load_to_target_table
from src.schemas.etl_config_schema import SourceRequest
from typing import List
import json

router = APIRouter(prefix="/pipeline", tags=["ETL Pipelines"])

# Új pipeline létrehozása
@router.post("/create", response_model=ETLConfigResponse)
def create_pipeline(config:  ETLConfigBase, db: Session = Depends(get_db)):
    try:
        accepted_fields = {
            "pipeline_name",
            "source",
            "schedule",
            "custom_time",
            "condition",
            "uploaded_file_path",
            "uploaded_file_name",
            "dependency_pipeline_id",
            "field_mappings",
            "transformation",
            "selected_columns",
            "group_by_columns",
            "order_by_column",
            "order_direction",
            "custom_sql",
            "update_mode",
            "save_option",
            "column_order"
        }
        schema = db.query(APISchema).filter_by(source=config.source).first()
        if not schema:
            raise HTTPException(status_code=404, detail="No schema found for the selected source.")
        # 2. Egyedi tábla-név generálása
        table_name = generate_table_name(config.pipeline_name, version=1)
        # 3. Tábla létrehozása a sémából
        create_table_from_schema(table_name, schema.field_mappings, db)
        # 4. Adat beállítása és mentése
        filtered_data = {k: v for k, v in config.dict().items() if k in accepted_fields}
        filtered_data["target_table_name"] = table_name
        new_pipeline = ETLConfig(**filtered_data, version=1)

        db.add(new_pipeline)
        db.commit()
        db.refresh(new_pipeline)
        print("Pipilne successfully created:", new_pipeline.pipeline_name)

        return new_pipeline

    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all", response_model=List[ETLConfigResponse])
def get_all_pipelines(db: Session = Depends(get_db)):
    return db.query(ETLConfig).all()


@router.put("/update/{pipeline_id}", response_model=ETLConfigResponse)
def update_pipeline(pipeline_id: int, config: ETLConfigUpdate, db: Session = Depends(get_db)):
    pipeline = db.query(ETLConfig).filter(ETLConfig.id == pipeline_id).first()

    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    for key, value in config.dict(exclude_unset=True).items():
        setattr(pipeline, key, value)

    pipeline.version += 1
    db.commit()
    db.refresh(pipeline)
    return pipeline

@router.post("/load/{pipeline_id}")
def run_pipeline_load(pipeline_id: int, db: Session = Depends(get_db)):
    try:
        load_to_target_table(pipeline_id, db)
        return {"message": "Data loaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/available-sources", response_model=List[str])
def get_available_sources(db: Session = Depends(get_db)):
    sources = db.query(APISchema.source).all()
    return [row[0] for row in sources]

@router.post("/load-schema")
def load_schema(req: SourceRequest, db: Session = Depends(get_db)):
    normalized_source = req.source.strip().rstrip('/')
    schema = db.query(APISchema).filter(APISchema.source == normalized_source).first()

    if not schema:
        raise HTTPException(status_code=404, detail="Schema not found.")

    # Ha string, dekódoljuk
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

