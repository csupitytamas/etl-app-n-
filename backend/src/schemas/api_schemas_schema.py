from pydantic import BaseModel
from typing import List

class APISchemaField(BaseModel):
    name: str
    type: str

class APISchemaBase(BaseModel):
    source: str
    field_mappings: List[APISchemaField]
    alias: str | None = None
    description: str | None = None

class SourceRequest(BaseModel):
    source: str

class SourceAlias(BaseModel):
    source: str
    alias: str | None = None
    description: str | None = None

    model_config = {
        "from_attributes": True}



