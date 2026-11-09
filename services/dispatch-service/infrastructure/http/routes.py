from fastapi import APIRouter, status
from application.commands.create_dispatch_command import CreateDispatchCommand
from application.responses.dispatch_response import DispatchResponse
from application.use_cases.create_dispatch_use_case import CreateDispatchUseCase
from application.use_cases.get_dispatch_use_case import GetDispatchUseCase

def create_dispatch_router(
    create_uc: CreateDispatchUseCase,
    get_uc: GetDispatchUseCase,
) -> APIRouter:
    router = APIRouter(prefix="/dispatches", tags=["Dispatches"])

    @router.post("", response_model=DispatchResponse, status_code=status.HTTP_201_CREATED)
    def create_dispatch(command: CreateDispatchCommand):
        return create_uc.execute(command)

    @router.get("/{dispatch_id}", response_model=DispatchResponse)
    def get_dispatch(dispatch_id: str):
        return get_uc.execute(dispatch_id)

    return router
