from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from src.schemas import  ETLConfigBase, ETLConfigUpdate, ETLConfigResponse
from src.db.connection import get_db
from src.models import ETLConfig, APISchema
from src.utils.db_creation_util import generate_table_name
from src.constans.accepted_fields import ACCEPTED_ETL_FIELDS


router = APIRouter()

@router.post("/create", response_model=ETLConfigResponse)
def create_pipeline(config:  ETLConfigBase, db: Session = Depends(get_db)):
    try:
        schema = db.query(APISchema).filter_by(source=config.source).first()
        if not schema:
            raise HTTPException(status_code=404, detail="No schema found for the selected source.")
        table_name = generate_table_name(config.pipeline_name, version=1)
        filtered_data = {k: v for k, v in config.dict().items() if k in ACCEPTED_ETL_FIELDS}
        filtered_data["target_table_name"] = table_name
        new_pipeline = ETLConfig(**filtered_data, version=1)

        db.add(new_pipeline)
        db.commit()
        db.refresh(new_pipeline)
        print("Pipeline successfully created:", new_pipeline.pipeline_name)

        return new_pipeline

    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all", response_model=list[ETLConfigResponse])
def get_all_pipelines(db: Session = Depends(get_db)):
    pipelines = db.query(ETLConfig).all()
    return pipelines

@router.post("/load/{pipeline_id}", response_model=ETLConfigResponse)
def load_pipeline_data(pipeline_id: int, db: Session = Depends(get_db)):
    pipeline = db.query(ETLConfig).filter(ETLConfig.id == pipeline_id).first()

    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    return pipeline


@router.post("/updated_pipeline/{pipeline_id}", response_model=ETLConfigResponse)
def updated_pipeline(pipeline_id: int, config: ETLConfigUpdate, db: Session = Depends(get_db)):
    old_pipeline = db.query(ETLConfig).filter(ETLConfig.id == pipeline_id).first()

    if not old_pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    updated_data = config.dict(exclude_unset=True)
    updated_data['source'] = old_pipeline.source
    new_version = old_pipeline.version + 1
    new_pipeline_name = f"{old_pipeline.pipeline_name} v{new_version}"
    new_table_name = generate_table_name(new_pipeline_name, new_version)

    new_pipeline = ETLConfig(
        **updated_data,
        pipeline_name=new_pipeline_name,     # EZ az új név kell!
        version=new_version,
        target_table_name=new_table_name
    )

    db.add(new_pipeline)
    db.commit()
    db.refresh(new_pipeline)
    return new_pipeline
