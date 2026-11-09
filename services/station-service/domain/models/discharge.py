from dataclasses import dataclass
from datetime import datetime

@dataclass
class Discharge:
    id: str
    dispatch_id: str
    station_id: str
    tank_id: str
    received_volume_liters: float
    received_temperature_c: float
    discharged_at: datetime
