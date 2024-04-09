from app.domain.models.driver_assignment import DriverAssignmentModel, LocationModel, DriverAssignmentIdModel
from datetime import date


class DriverAssignmentRepository:
    def assign_driver_to_vehicle(self, driver_assignment: DriverAssignmentModel) -> DriverAssignmentModel:
        raise NotImplementedError(
            "Method assign_driver_to_vehicle hasn't been implemented yet."
        )


    def get_active_driver_assignments_with_driver_id_or_vehicle_id_at_date(
            self, driver_id: int, vehicle_id: int, travel_date: date
    ) -> list[DriverAssignmentModel]:
        raise NotImplementedError(
            "Method get_driver_assignments_with_driver_id_or_vehicle_id_at_date hasn't been implemented yet."
        )

    def get_active_driver_assignment_by_destination_location_at_date(
            self, location: LocationModel, travel_date: date, exclude_assignment: DriverAssignmentIdModel
    ) -> DriverAssignmentModel:
        raise NotImplementedError(
            "Method get_driver_assignment_by_destination_location_at_date hasn't been implemented yet."
        )
