from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

class ChartDataItem(BaseModel):
    name: str
    value: float

class ChartResponse(BaseModel):
    chart_type: str
    title: str
    x_axis_data: List[str]
    series: List[dict]

class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None
    timestamp: datetime
