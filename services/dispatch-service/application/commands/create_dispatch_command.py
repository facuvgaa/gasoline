from pydantic import BaseModel, Field
from domain.models.dispatch import FuelType

class CreateDispatchCommand(BaseModel):
    truck_plate: str = Field(..., min_length=1, description="Patente del camión")
    driver_id: str = Field(..., min_length=1, description="ID del chofer")
    fuel_type: FuelType = Field(..., description="Tipo de combustible")
    volume_liters: float = Field(..., gt=0, description="Volumen cargado en litros (debe ser > 0)")
    temperature_c: float = Field(..., description="Temperatura del despacho en °C")
