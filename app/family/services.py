from app.models import Family
from app.extensions import db
from flask import session
from app.services.service_base import service_response
from typing import Tuple

class FamilyService:
    @staticmethod
    def get_family_by_id(family_id: int) -> Tuple[dict, int]:
        """
        Retrieves a family by its id.

        Args:
            family_id (int): The id of the family to retrieve.

        Returns:
            Tuple[dict, int]: A tuple containing a dictionary and HTTP status code.
        """
        try:
            family = db.session.query(Family).filter_by(family_id=family_id).first()
            if family:
                return service_response(200, "Family found", "success", family)
            else:
                return service_response(404, "Family not found", "warning", None)
        except Exception as e:
            # Todo: log the error
            return service_response(500, "Something went wrong", "error", None)

    @staticmethod
    def get_user_families(user_id: int) -> Tuple[dict, int]:
        """
        Retrieves all families for a user.

        Args:
            user_id (int): The id of the user.

        Returns:
            Tuple[dict, int]: A tuple containing a dictionary and HTTP status code.

        """
        try:
            families = db.session.query(Family).filter_by(user_id=user_id).all()
            if families:
                return service_response(200, "Families found", "success", families)
            else:
                return service_response(404, "No families found", "warning", None)
        except Exception as e:
            # Todo: log the error
            return service_response(500, "Something went wrong", "error", None)