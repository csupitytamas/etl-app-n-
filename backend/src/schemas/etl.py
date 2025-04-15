import datetime

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

class PipeLine(BaseModel):
    name_field: str
    source_field: str

class EtlConfig(BaseModel):
    schedule: str
    custom_time: Optional[datetime] = None
    running_condition: Optional[str] = None
    transformation: Optional[str] = None
    update: str
    save: str
    uploaded_file_name: Optional[str] = None





