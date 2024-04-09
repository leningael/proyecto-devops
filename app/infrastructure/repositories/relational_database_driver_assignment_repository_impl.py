from datetime import date
from pymysql import IntegrityError
from sqlmodel import Session, select, or_
from app.domain.exceptions.resource_not_found_exception import ResourceNotFoundException
from app.domain.models.driver_assignment import DriverAssignmentModel, LocationModel, DriverAssignmentIdModel
from app.infrastructure.configs.sql_database import db_engine

from app.application.repositories.driver_assingment_repository import DriverAssignmentRepository
from app.infrastructure.entities.driver_assignment_entity import DriverAssignment
from app.infrastructure.mappers.driver_assignment_mappers import \
    map_driver_assignment_entity_to_driver_assignment_model, map_driver_assignment_model_to_driver_assignment_entity


class RelationalDatabaseDriverAssignmentRepositoryImpl(DriverAssignmentRepository):
    def assign_driver_to_vehicle(self, driver_assignment: DriverAssignmentModel) -> DriverAssignmentModel:
        with Session(db_engine) as session:
            driver_assignment_entity = map_driver_assignment_model_to_driver_assignment_entity(driver_assignment)
            session.add(driver_assignment_entity)
            try:
                session.commit()
            except IntegrityError:
                session.rollback()
                raise ResourceNotFoundException("Driver or vehicle to assign not found")
            else:
                session.refresh(driver_assignment_entity)
        return map_driver_assignment_entity_to_driver_assignment_model(driver_assignment_entity)

    def get_active_driver_assignments_with_driver_id_or_vehicle_id_at_date(
            self, driver_id: int, vehicle_id: int, travel_date: date
    ) -> list[DriverAssignmentModel]:
        with Session(db_engine) as session:
            driver_assignment_entities = session.exec(
                select(DriverAssignment).where(
                    or_(
                        DriverAssignment.driver_id == driver_id,
                        DriverAssignment.vehicle_id == vehicle_id
                    ),
                    DriverAssignment.travel_date == travel_date,
                    DriverAssignment.active == True
                )
            ).all()
        return [
            map_driver_assignment_entity_to_driver_assignment_model(driver_assignment_entity)
            for driver_assignment_entity in driver_assignment_entities
        ]

    def get_active_driver_assignment_by_destination_location_at_date(
            self, location: LocationModel, travel_date: date, exclude_assignment: DriverAssignmentIdModel
    ) -> DriverAssignmentModel:
        with Session(db_engine) as session:
            statement = select(DriverAssignment).where(
                DriverAssignment.destination_location_latitude == location.latitude,
                DriverAssignment.destination_location_longitude == location.longitude,
                DriverAssignment.travel_date == travel_date,
                DriverAssignment.active == True
            )
            if exclude_assignment:
                statement = statement.where(
                    DriverAssignment.driver_id != exclude_assignment.driver_id,
                    DriverAssignment.vehicle_id != exclude_assignment.vehicle_id,
                )
            driver_assignment_entity = session.exec(statement).first()
        if driver_assignment_entity:
            return map_driver_assignment_entity_to_driver_assignment_model(driver_assignment_entity)
