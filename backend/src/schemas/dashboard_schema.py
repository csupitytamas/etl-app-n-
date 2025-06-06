from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class DashboardPipelineResponse(BaseModel):
    id: int
    name: str
    lastRun: Optional[str]
    status: Optional[str]
    nextRun: Optional[str]
    source: str
    alias: Optional[str]
    sampleData: List[Dict[str, Any]]

    class Config:  # <<< FONTOS
        from_attributes = True

DashboardListResponse = List[DashboardPipelineResponse]