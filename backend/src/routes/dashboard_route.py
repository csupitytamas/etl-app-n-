from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from src.models import Status, ETLConfig, APISchema
from src.schemas  import DashboardPipelineResponse
from src.db.connection import get_db
import pandas as pd  # Ha szeretnéd, de SQLAlchemy raw query is jó

router = APIRouter()


@router.get("/dashboard", response_model=list[DashboardPipelineResponse])
def get_dashboard(db: Session = Depends(get_db)):
    pipelines = (
        db.query(ETLConfig)
        .outerjoin(Status, ETLConfig.id == Status.etlconfig_id)
        .outerjoin(APISchema, ETLConfig.source == APISchema.source)
        .options(joinedload(ETLConfig.schema))
        .options(joinedload(ETLConfig.status))  # Fontos a status is!
        .all()
    )

    result = []
    for pipeline in pipelines:
        sample_data = []
        if pipeline.target_table_name:
            try:
                sql = f"SELECT * FROM {pipeline.target_table_name}"
                df = pd.read_sql(sql, db.bind)
                sample_data = df.to_dict(orient="records")
            except Exception:
                sample_data = []

        # Itt választjuk ki az első státuszt
        status = pipeline.status[0] if pipeline.status else None

        result.append({
            "id": pipeline.id,
            "name": pipeline.pipeline_name,
            "lastRun": status.last_successful_run.strftime("%Y-%m-%d %H:%M") if status and status.last_successful_run else None,
            "status": status.current_status if status else None,
            "nextRun": status.next_scheduled_run.strftime("%Y-%m-%d %H:%M") if status and status.next_scheduled_run else None,
            "source": pipeline.source,
            "alias": pipeline.schema.alias if pipeline.schema else None,
            "sampleData": sample_data
        })
    return result