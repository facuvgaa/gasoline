from fastapi import APIRouter, status
from application.commands.record_discharge_command import RecordDischargeCommand
from application.responses.discharge_response import DischargeResponse
from application.use_cases.record_discharge_use_case import RecordDischargeUseCase
from application.use_cases.get_discharge_use_case import GetDischargeUseCase

def create_discharge_router(
    record_uc: RecordDischargeUseCase,
    get_uc: GetDischargeUseCase,
) -> APIRouter:
    router = APIRouter(prefix="/discharges", tags=["Discharges"])

    @router.post("", response_model=DischargeResponse, status_code=status.HTTP_201_CREATED)
    def record_discharge(command: RecordDischargeCommand):
        return record_uc.execute(command)

    @router.get("/{discharge_id}", response_model=DischargeResponse)
    def get_discharge_by_id(discharge_id: str):
        return get_uc.execute_by_id(discharge_id)

    @router.get("/by-dispatch/{dispatch_id}", response_model=DischargeResponse)
    def get_discharge_by_dispatch_id(dispatch_id: str):
        return get_uc.execute_by_dispatch_id(dispatch_id)

    return router
