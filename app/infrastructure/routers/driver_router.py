from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status

from app.application.services.driver_service import DriverService
from app.domain.exceptions.conflict_with_existing_resource_exception import (
    ConflictWithExistingResourceException,
)
from app.domain.exceptions.resource_not_found_exception import ResourceNotFoundException
from app.infrastructure.dto.driver_dto import DriverDTO
from app.infrastructure.dto.driver_request_dto import DriverRequestDTO
from app.infrastructure.mappers.driver_mappers import (
    map_driver_dto_to_driver_model,
    map_driver_model_to_driver_dto,
    map_driver_request_dto_to_driver_model,
)
from app.infrastructure.middlewares.protect_route_middleware import (
    protect_route_middlware,
)
from app.infrastructure.repositories.relational_database_driver_repository_impl import (
    RelationalDatabaseDriverRepositoryImpl,
)


driver_router = APIRouter(dependencies=[Depends(protect_route_middlware)])
driver_service = DriverService(
    driver_repository=RelationalDatabaseDriverRepositoryImpl()
)


@driver_router.get("/{driver_id}", status_code=status.HTTP_200_OK)
def get_driver_by_driver_id(driver_id: int) -> DriverDTO:
    try:
        return map_driver_model_to_driver_dto(
            driver_service.get_driver_by_driver_id(driver_id)
        )
    except ResourceNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found",
        )


@driver_router.get("", status_code=status.HTTP_200_OK)
def get_all_drivers() -> list[DriverDTO]:
    return [
        map_driver_model_to_driver_dto(driver)
        for driver in driver_service.get_all_drivers()
    ]


@driver_router.post("", status_code=status.HTTP_201_CREATED)
def create_driver(driver_request_dto: DriverRequestDTO) -> DriverDTO:
    try:
        return map_driver_model_to_driver_dto(
            driver_service.create_driver(
                driver=map_driver_request_dto_to_driver_model(driver_request_dto)
            )
        )
    except ConflictWithExistingResourceException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A driver with the curp entered is already registered",
        )


@driver_router.put("", status_code=status.HTTP_200_OK)
def edit_driver_information(driver_dto: DriverDTO) -> DriverDTO:
    try:
        return map_driver_model_to_driver_dto(
            driver_service.update_driver(
                driver=map_driver_dto_to_driver_model(driver_dto),
            )
        )
    except ResourceNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found",
        )


@driver_router.delete("/{driver_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_driver(driver_id: int) -> None:
    try:
        driver_service.delete_driver_by_driver_id(driver_id)
    except ResourceNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found",
        )