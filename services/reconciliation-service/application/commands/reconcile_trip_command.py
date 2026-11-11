from pydantic import BaseModel, Field


class ReconcileTripCommand(BaseModel):
    dispatch_id: str = Field(..., min_length=1)
    truck_plate: str = Field(..., min_length=1)
    

    dispatched_volume: float = Field(..., gt=0)
    dispatched_temp_c: float
    

    received_volume: float = Field(..., gt=0)
    received_temp_c: float
    

    valve_opened_in_transit: bool = False
    max_speed_kmh: float = 0.0