import pytest
from pydantic import ValidationError

from domain.models.discharge import Discharge
from domain.ports.repository import DischargeRepositoryPort
from domain.exceptions.exceptions import DischargeNotFoundException

from application.commands.record_discharge_command import RecordDischargeCommand
from application.use_cases.record_discharge_use_case import RecordDischargeUseCase
from application.use_cases.get_discharge_use_case import GetDischargeUseCase

# 1. Fake Repository en memoria
class FakeDischargeRepository(DischargeRepositoryPort):
    def __init__(self):
        self.discharges: dict[str, Discharge] = {}

    def save(self, discharge: Discharge) -> None:
        self.discharges[discharge.id] = discharge

    def find_by_id(self, discharge_id: str) -> Discharge | None:
        return self.discharges.get(discharge_id)

    def find_by_dispatch_id(self, dispatch_id: str) -> Discharge | None:
        for d in self.discharges.values():
            if d.dispatch_id == dispatch_id:
                return d
        return None

# 2. Test caso exitoso
def test_record_discharge_successfully():
    repo = FakeDischargeRepository()
    use_case = RecordDischargeUseCase(repository=repo)

    cmd = RecordDischargeCommand(
        dispatch_id="DISP-UUID-1234",
        station_id="ESTACION-CORDOBA-01",
        tank_id="TANQUE-01-NAFTA",
        received_volume_liters=24900.0,
        received_temperature_c=22.0,
    )

    response = use_case.execute(cmd)

    assert response.id is not None
    assert response.dispatch_id == "DISP-UUID-1234"
    assert response.received_volume_liters == 24900.0
    assert response.station_id == "ESTACION-CORDOBA-01"

    # Verificar que se guardó en repo
    saved = repo.find_by_id(response.id)
    assert saved is not None
    assert saved.tank_id == "TANQUE-01-NAFTA"

# 3. Test falla por volumen inválido (Validación de Command)
def test_record_discharge_fails_negative_volume():
    with pytest.raises(ValidationError):
        RecordDischargeCommand(
            dispatch_id="DISP-UUID-1234",
            station_id="ESTACION-01",
            tank_id="TANQUE-01",
            received_volume_liters=-100.0,
            received_temperature_c=20.0,
        )

# 4. Test no encontrado
def test_get_discharge_not_found():
    repo = FakeDischargeRepository()
    get_use_case = GetDischargeUseCase(repository=repo)

    with pytest.raises(DischargeNotFoundException):
        get_use_case.execute_by_id("id-fantasma")
