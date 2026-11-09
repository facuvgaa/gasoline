import pytest   
from pydantic import ValidationError


from domain.models.dispatch import Dispatch, FuelType
from domain.ports.repository import DispatchRepositoryPort
from domain.exceptions.exceptions import  DispatchNotFoundException

from application.commands.create_dispatch_command import CreateDispatchCommand
from application.use_cases.create_dispatch_use_case import CreateDispatchUseCase
from application.use_cases.get_dispatch_use_case import GetDispatchUseCase



class DispatchTest(DispatchRepositoryPort):
    def __init__(self):
        self.dispatches: dict[str, Dispatch] = {}


    def save(self, dispatch)-> None:
        self.dispatches[dispatch.id] = dispatch

    def find_by_id(self, dispatch_id: str) -> Dispatch | None:
        return self.dispatches.get(dispatch_id)


def test_create_dispatch_successfully():
    fake_repo = DispatchTest()
    use_case = CreateDispatchUseCase(repository=fake_repo)
    command = CreateDispatchCommand(
        truck_plate="AB123CD",
        driver_id="CHOFER-99",
        fuel_type=FuelType.NAFTA_SUPER,
        volume_liters=20000.0,
        temperature_c=17.5,
    )

    response = use_case.execute(command)

    assert response.id is not None
    assert response.truck_plate == "AB123CD"
    assert response.volume_liters == 20000.0
    assert response.status == "LOADED"

    saved = fake_repo.find_by_id(response.id)
    assert saved is not None
    assert saved.driver_id == "CHOFER-99"

def test_create_dispatch_fails_with_negative_volume():
    fake_repo = DispatchTest()
    use_case = CreateDispatchUseCase(repository=fake_repo)

    with pytest.raises(ValidationError):
        CreateDispatchCommand(
            truck_plate="AB123CD",
            driver_id="CHOFER-99",
            fuel_type=FuelType.NAFTA_SUPER,
            volume_liters=-500.0, 
            temperature_c=17.5,
        )
def test_get_dispatch_not_found():
    fake_repo = DispatchTest()
    get_use_case = GetDispatchUseCase(repository=fake_repo)
    with pytest.raises(DispatchNotFoundException):
        get_use_case.execute("id-inexistente-123")  