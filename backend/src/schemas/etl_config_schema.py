from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Dict, Any, List


class ETLConfigBase(BaseModel):
    pipeline_name: str
    source: str
    schedule: str
    custom_time: Optional[str] = None
    condition: Optional[str] = None

    uploaded_file_path: Optional[str] = None
    uploaded_file_name: Optional[str] = None
    dependency_pipeline_id: Optional[str] = None

    field_mappings: Optional[Dict[str, Any]] = None
    transformation: Optional[Dict[str, Any]] = None
    selected_columns: Optional[List[str]] = None
    group_by_columns: Optional[List[str]] = None

    order_by_column: Optional[str] = None
    order_direction: Optional[str] = None
    custom_sql: Optional[str] = None

    update_mode: str
    save_option: str

    column_order: Optional[List[str]] = None


class ETLConfigUpdate(ETLConfigBase):
    pipeline_name: Optional[str] = None
    source: Optional[str] = None
    schedule: Optional[str] = None
    update_mode: Optional[str] = None
    save_option: Optional[str] = None


class ETLConfigResponse(ETLConfigBase):
    id: int
    version: int
    created_at: datetime
    modified_at: datetime

    class Config:
        from_attributes = True
