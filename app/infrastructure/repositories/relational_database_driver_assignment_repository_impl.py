from datetime import date
from pymysql import IntegrityError
from sqlmodel import Session, select, or_
from app.domain.exceptions.resource_not_found_exception import ResourceNotFoundException
from app.domain.models.driver_assignment import (
    DriverAssignmentModel,
    LocationModel,
    DriverAssignmentIdModel,
)
from app.infrastructure.configs.sql_database import db_engine
from loguru import logger

from app.application.repositories.driver_assingment_repository import (
    DriverAssignmentRepository,
)
from app.infrastructure.entities.driver_assignment_entity import DriverAssignment
from app.infrastructure.mappers.driver_assignment_mappers import (
    map_driver_assignment_entity_to_driver_assignment_model,
    map_driver_assignment_model_to_driver_assignment_entity,
)


class RelationalDatabaseDriverAssignmentRepositoryImpl(DriverAssignmentRepository):

    def assign_driver_to_vehicle(
        self, driver_assignment: DriverAssignmentModel
    ) -> DriverAssignmentModel:
        logger.debug("Method called: relational_database_driver_assignment_repository_impl.assign_driver_to_vehicle()")
        logger.debug(f"Params passed: {driver_assignment.__dict__}")
        with Session(db_engine) as session:
            driver_assignment_entity = (
                map_driver_assignment_model_to_driver_assignment_entity(
                    driver_assignment
                )
            )
            session.add(driver_assignment_entity)
            try:
                session.commit()
            except IntegrityError:
                session.rollback()
                raise ResourceNotFoundException("Driver or vehicle to assign not found")
            else:
                session.refresh(driver_assignment_entity)
            return map_driver_assignment_entity_to_driver_assignment_model(
                driver_assignment_entity
            )

    def get_driver_assignments(
        self, only_actives: bool, travel_date: date | None
    ) -> list[DriverAssignmentModel]:
        logger.debug("Method called: relational_database_driver_assignment_repository_impl.get_driver_assignments()")
        logger.debug(f"Params passed: {only_actives} and {travel_date}")
        with Session(db_engine) as session:
            statement = select(DriverAssignment)
            if travel_date:
                statement = statement.where(DriverAssignment.travel_date == travel_date)
            if only_actives:
                statement = statement.where(DriverAssignment.active)
            driver_assignment_entities = session.exec(
                statement.order_by(
                    DriverAssignment.travel_date.desc(),
                    DriverAssignment.creation_date.desc(),
                )
            ).all()
            return [
                map_driver_assignment_entity_to_driver_assignment_model(
                    driver_assignment_entity
                )
                for driver_assignment_entity in driver_assignment_entities
            ]

    def get_driver_assignment(
        self, driver_id: int, vehicle_id: int, travel_date: date
    ) -> DriverAssignmentModel:
        logger.debug("Method called: relational_database_driver_assignment_repository_impl.get_driver_assignment()")
        logger.debug(f"Params passed: {driver_id}, {vehicle_id}, {travel_date}")
        with Session(db_engine) as session:
            driver_assignment_entity = session.get(
                DriverAssignment, (driver_id, vehicle_id, travel_date)
            )
            if driver_assignment_entity:
                return map_driver_assignment_entity_to_driver_assignment_model(
                    driver_assignment_entity
                )

    def get_active_driver_assignments_with_driver_id_or_vehicle_id_at_date(
        self, driver_id: int, vehicle_id: int, travel_date: date
    ) -> list[DriverAssignmentModel]:
        logger.debug("Method called: relational_database_driver_assignment_repository_impl.get_active_driver_assignments_with_driver_id_or_vehicle_id_at_date()")
        logger.debug(f"Params passed: {driver_id}, {vehicle_id}, {travel_date}")
        with Session(db_engine) as session:
            driver_assignment_entities = session.exec(
                select(DriverAssignment).where(
                    or_(
                        DriverAssignment.driver_id == driver_id,
                        DriverAssignment.vehicle_id == vehicle_id,
                    ),
                    DriverAssignment.travel_date == travel_date,
                    DriverAssignment.active,
                )
            ).all()
        return [
            map_driver_assignment_entity_to_driver_assignment_model(
                driver_assignment_entity
            )
            for driver_assignment_entity in driver_assignment_entities
        ]

    def get_active_driver_assignment_by_destination_location_at_date(
        self,
        location: LocationModel,
        travel_date: date,
        exclude_assignment: DriverAssignmentIdModel | None,
    ) -> DriverAssignmentModel:
        logger.debug("Method called: relational_database_driver_assignment_repository_impl.get_active_driver_assignment_by_destination_location_at_date()")
        logger.debug(f"Params passed: {location.__dict__}, {travel_date}")
        with Session(db_engine) as session:
            statement = select(DriverAssignment).where(
                DriverAssignment.destination_location_latitude == location.latitude,
                DriverAssignment.destination_location_longitude == location.longitude,
                DriverAssignment.travel_date == travel_date,
                DriverAssignment.active,
            )
            if exclude_assignment:
                statement = statement.where(
                    DriverAssignment.driver_id != exclude_assignment.driver_id,
                    DriverAssignment.vehicle_id != exclude_assignment.vehicle_id,
                )
            driver_assignment_entity = session.exec(statement).first()
        if driver_assignment_entity:
            return map_driver_assignment_entity_to_driver_assignment_model(
                driver_assignment_entity
            )

    def update_driver_assignment(
        self, driver_assignment: DriverAssignmentModel
    ) -> DriverAssignmentModel:
        logger.debug("Method called: relational_database_driver_assignment_repository_impl.update_driver_assignment()")
        logger.debug(f"Params passed: {driver_assignment.__dict__}")
        with Session(db_engine) as session:
            driver_assignment_entity = session.get(
                DriverAssignment,
                (
                    driver_assignment.driver_id,
                    driver_assignment.vehicle_id,
                    driver_assignment.travel_date,
                ),
            )
            if driver_assignment_entity:
                driver_assignment_entity.route_name = driver_assignment.route_name
                driver_assignment_entity.origin_location_latitude = (
                    driver_assignment.origin_location.latitude
                )
                driver_assignment_entity.origin_location_longitude = (
                    driver_assignment.origin_location.longitude
                )
                driver_assignment_entity.destination_location_latitude = (
                    driver_assignment.destination_location.latitude
                )
                driver_assignment_entity.destination_location_longitude = (
                    driver_assignment.destination_location.longitude
                )
                driver_assignment_entity.completed_successfully = (
                    driver_assignment.completed_successfully
                )
                driver_assignment_entity.problem_description = (
                    driver_assignment.problem_description
                )
                driver_assignment_entity.comments = driver_assignment.comments
                session.add(driver_assignment_entity)
                session.commit()
                session.refresh(driver_assignment_entity)
        if driver_assignment_entity:
            return map_driver_assignment_entity_to_driver_assignment_model(
                driver_assignment_entity
            )

    def set_driver_assignment_as_inactive(
        self, driver_id: int, vehicle_id: int, travel_date: date
    ) -> None:
        logger.debug("Method called: relational_database_driver_assignment_repository_impl.set_driver_assignment_as_inactive()")
        logger.debug(f"Params passed: {driver_id}, {vehicle_id}, {travel_date}")
        with Session(db_engine) as session:
            driver_assignment_entity = session.get(
                DriverAssignment, (driver_id, vehicle_id, travel_date)
            )
            if driver_assignment_entity:
                driver_assignment_entity.active = False
                session.commit()

    def get_all_assignments_for_driver(
        self, driver_id: int
    ) -> list[DriverAssignmentModel]:
        logger.debug("Method called: relational_database_driver_assignment_repository_impl.get_all_assignments_for_driver()")
        logger.debug(f"Params passed: {driver_id}")
        with Session(db_engine) as session:
            driver_assignment_entities = session.exec(
                select(DriverAssignment).where(DriverAssignment.driver_id == driver_id)
            ).all()
        return [
            map_driver_assignment_entity_to_driver_assignment_model(
                driver_assignment_entity
            )
            for driver_assignment_entity in driver_assignment_entities
        ]

    def get_all_assignments_for_vehicle(
        self, vehicle_id: int
    ) -> list[DriverAssignmentModel]:
        logger.debug("Method called: relational_database_driver_assignment_repository_impl.get_all_assignments_for_vehicle()")
        logger.debug(f"Params passed: {vehicle_id}")
        with Session(db_engine) as session:
            driver_assignment_entities = session.exec(
                select(DriverAssignment).where(
                    DriverAssignment.vehicle_id == vehicle_id
                )
            ).all()
        return [
            map_driver_assignment_entity_to_driver_assignment_model(
                driver_assignment_entity
            )
            for driver_assignment_entity in driver_assignment_entities
        ]

    def get_number_of_today_assignments(self) -> int:
        logger.debug("Method called: relational_database_driver_assignment_repository_impl.get_number_of_today_assignments()")
        today = date.today()
        formatted_date = today.strftime("%Y-%m-%d")
        with Session(db_engine) as session:
            number_of_assignments = len(
                session.exec(
                    select(DriverAssignment).where(
                        DriverAssignment.travel_date == formatted_date
                    )
                ).all()
            )
        return number_of_assignments
