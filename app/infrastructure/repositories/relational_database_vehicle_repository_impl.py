from sqlmodel import Session, select
from typing import List
from loguru import logger

from app.application.repositories.vehicle_repository import (
    VehicleRepository,
)
from app.infrastructure.configs.sql_database import db_engine
from app.infrastructure.entities.vehicle_entity import Vehicle
from app.domain.models.vehicle_model import VehicleModel
from app.infrastructure.mappers.vehicle_mappers import (
    map_vehicle_entity_to_vehicle_model,
    map_vehicle_model_to_vehicle_entity,
)


class RelationalDatabaseVehicleRepositoryImpl(VehicleRepository):

    def get_vehicle_by_id(self, id: int) -> VehicleModel | None:
        logger.debug("Method called: relational_database_vehicle_repository_impl.get_vehicle_by_id()")
        logger.debug(f"Params passed: {id}")
        with Session(db_engine) as session:
            vehicle_entity = session.exec(
                select(Vehicle).where(Vehicle.id == id)
            ).first()

            if vehicle_entity:
                return map_vehicle_entity_to_vehicle_model(vehicle_entity)

    def get_vehicle_by_vin(self, vin: str) -> VehicleModel | None:
        logger.debug("Method called: relational_database_vehicle_repository_impl.get_vehicle_by_vin()")
        logger.debug(f"Params passed: {vin}")
        with Session(db_engine) as session:
            vehicle_entity = session.exec(
                select(Vehicle).where(Vehicle.vin == vin)
            ).first()
            if vehicle_entity:
                return map_vehicle_entity_to_vehicle_model(vehicle_entity)

    def get_vehicle_by_plate(self, plate: str) -> VehicleModel | None:
        logger.debug("Method called: relational_database_vehicle_repository_impl.get_vehicle_by_plate()")
        logger.debug(f"Params passed: {plate}")
        with Session(db_engine) as session:
            vehicle_entity = session.exec(
                select(Vehicle).where(Vehicle.plate == plate)
            ).first()
            if vehicle_entity:
                return map_vehicle_entity_to_vehicle_model(vehicle_entity)

    def get_vehicles(self) -> List[VehicleModel] | None:
        logger.debug("Method called: relational_database_vehicle_repository_impl.get_vehicles()")
        with Session(db_engine) as session:
            vehicles = session.exec(select(Vehicle))

            if vehicles:
                return [
                    map_vehicle_entity_to_vehicle_model(vehicle) for vehicle in vehicles
                ]

    def remove_vehicle_by_id(self, id: int) -> int | None:
        logger.debug("Method called: relational_database_vehicle_repository_impl.remove_vehicle_by_id()")
        logger.debug(f"Params passed: {id}")
        with Session(db_engine) as session:
            vehicle_entity = session.exec(select(Vehicle).where(Vehicle.id == id)).one()

            session.delete(vehicle_entity)
            session.commit()

    def update_vehicle(self, vehicle_update: VehicleModel, id: int):
        logger.debug("Method called: relational_database_vehicle_repository_impl.update_vehicle()")
        logger.debug(f"Params passed: ID: {id} and {vehicle_update.__dict__}")
        with Session(db_engine) as session:
            vehicle_entity = session.exec(select(Vehicle).where(Vehicle.id == id)).one()

            vehicle_entity.brand = vehicle_update.brand
            vehicle_entity.model = vehicle_update.model
            vehicle_entity.vin = vehicle_update.vin
            vehicle_entity.plate = vehicle_update.plate
            vehicle_entity.purchase_date = vehicle_update.purchase_date
            vehicle_entity.cost = vehicle_update.cost
            vehicle_entity.picture = vehicle_update.picture

            session.add(vehicle_entity)
            session.commit()
            session.refresh(vehicle_entity)
        return map_vehicle_entity_to_vehicle_model(vehicle_entity=vehicle_entity)

    def create_vehicle(self, vehicle: VehicleModel) -> VehicleModel:
        logger.debug("Method called: relational_database_vehicle_repository_impl.create_vehicle()")
        logger.debug(f"Params passed: {vehicle.__dict__}")
        with Session(db_engine) as session:
            vehicle_entity = map_vehicle_model_to_vehicle_entity(vehicle)

            session.add(vehicle_entity)
            session.commit()
            session.refresh(vehicle_entity)
            return map_vehicle_entity_to_vehicle_model(vehicle_entity)

    def get_number_of_vehicles(self) -> int:
        logger.debug("Method called: relational_database_vehicle_repository_impl.get_number_of_vehicles()")
        with Session(db_engine) as session:
            number_of_vehicles = len(session.exec(select(Vehicle)).all())
        return number_of_vehicles
