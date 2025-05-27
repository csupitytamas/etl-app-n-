from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from src.schemas.etl_config_schema import  ETLConfigBase, ETLConfigUpdate, ETLConfigResponse
from src.db.connection import get_db
from src.models.etl_config_model import ETLConfig
from typing import List

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

        filtered_data = {k: v for k, v in config.dict().items() if k in accepted_fields}
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

