from pydantic import BaseModel
from typing import List, Dict

class APISchemaField(BaseModel):
    name: str
    type: str

class APISchemaBase(BaseModel):
    source: str
    field_mappings: List[APISchemaField]

class SourceRequest(BaseModel):
    source: str