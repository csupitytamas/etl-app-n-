from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from src.schemas import  ETLConfigBase, ETLConfigUpdate, ETLConfigResponse
from src.db.connection import get_db
from src.models import ETLConfig, APISchema
from src.utils.db_creation_util import generate_table_name, create_table_from_schema
from src.constans.accepted_fields import ACCEPTED_ETL_FIELDS


router = APIRouter()

@router.post("/create", response_model=ETLConfigResponse)
def create_pipeline(config:  ETLConfigBase, db: Session = Depends(get_db)):
    try:
        schema = db.query(APISchema).filter_by(source=config.source).first()
        if not schema:
            raise HTTPException(status_code=404, detail="No schema found for the selected source.")
        table_name = generate_table_name(config.pipeline_name, version=1)
        create_table_from_schema(table_name, schema.field_mappings, db)
        filtered_data = {k: v for k, v in config.dict().items() if k in ACCEPTED_ETL_FIELDS}
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

