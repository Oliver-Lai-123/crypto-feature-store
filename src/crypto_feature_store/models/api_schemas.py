from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class PriceResponse(BaseModel):
    asset_id: str
    timestamp: datetime
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: float
    volume: Optional[float] = None


class FeatureResponse(BaseModel):
    asset_id: str
    timestamp: datetime
    close: float
    return_1: Optional[float] = None
    rolling_mean_24: Optional[float] = None
    rolling_std_24: Optional[float] = None
