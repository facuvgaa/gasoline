from pydantic import BaseModel, ConfigDict
from datetime import datetime

class DischargeResponse(BaseModel):
    id: str
    dispatch_id: str
    station_id: str
    tank_id: str
    received_volume_liters: float
    received_temperature_c: float
    discharged_at: datetime

    model_config = ConfigDict(from_attributes=True)
