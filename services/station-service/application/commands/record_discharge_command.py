from pydantic import BaseModel, Field

class RecordDischargeCommand(BaseModel):
    dispatch_id: str = Field(..., min_length=1, description="ID del despacho original")
    station_id: str = Field(..., min_length=1, description="Identificador de la estación de servicio")
    tank_id: str = Field(..., min_length=1, description="Identificador del tanque subterráneo receptor")
    received_volume_liters: float = Field(..., gt=0, description="Volumen medido recibido en litros (> 0)")
    received_temperature_c: float = Field(..., description="Temperatura del combustible al descargar (°C)")
