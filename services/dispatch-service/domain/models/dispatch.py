from enum import Enum
from dataclasses import dataclass
from datetime import datetime

class FuelType(str, Enum):
    NAFTA_SUPER = "NAFTA_SUPER"
    NAFTA_PREMIUM = "NAFTA_PREMIUM"
    DIESEL_500 = "DIESEL_500"

@dataclass
class Dispatch:
    id: str
    truck_plate: str
    driver_id: str
    fuel_type: FuelType
    volume_liters: float
    temperature_c: float
    status: str
    created_at: datetime
