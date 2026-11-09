from pydantic import BaseModel, ConfigDict
from datetime import datetime
from domain.models.dispatch import FuelType

class DispatchResponse(BaseModel):
    id: str
    truck_plate: str
    driver_id: str
    fuel_type: FuelType
    volume_liters: float
    temperature_c: float
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
