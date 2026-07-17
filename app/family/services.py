from app.models import Family
from app.extensions import db
from app.services.service_base import service_response
from typing import Tuple

class FamilyService:
    def __init__(self, db_session=None):
        self.db = db.session or db_session

    def get_family_by_id(self, family_id: int, user_id: int = None) -> Tuple[dict, int]:
        """
        Retrieves a family by its id.

        Args:
            family_id (int): The id of the family to retrieve.
            user_id (int): The id of user requesting access to family.
        Returns:
            Tuple[dict, int]: A tuple containing a dictionary and HTTP status code.
        """
        try:
            family = self.db.query(Family).filter_by(family_id=family_id).first()
            if not family:
                return service_response(404, "Family not found", "warning", None)
            elif user_id and family.user_id != user_id:
                return service_response(403, "You do not have permission to access this family", "danger", None)
            return service_response(200, "Family found", "success", family)
        except Exception as e:
            # Todo: log the error
            print(str(e))
            return service_response(500, "Something went wrong", "error", None)

    def get_user_families(self, user_id: int) -> Tuple[dict, int]:
        """
        Retrieves all families for a user.

        Args:
            user_id (int): The id of the user.

        Returns:
            Tuple[dict, int]: A tuple containing a dictionary and HTTP status code.

        """
        try:
            families = self.db.query(Family).filter_by(user_id=user_id).all()
            if families:
                return service_response(200, "Families found", "success", families)
            else:
                return service_response(404, "No families found", "warning", None)
        except Exception:
            # Todo: log the error
            return service_response(500, "Error retrieving families", "error", None)

    def create_family(self, family_name: str, user_id: int) -> Tuple[dict, int]:
        """
        Creates a new family.

        Args:
            family_name (str): The name of the family.
            user_id (int): The id of the user.

        Returns:
            Tuple[dict, int]: A tuple containing a dictionary and HTTP status code.
        """
        try:
            new_family = Family(name=family_name, user_id=user_id)
            self.db.add(new_family)
            self.db.commit()
            return service_response(201, "Family created successfully", "success", new_family)
        except Exception:
            self.db.rollback()
            # Todo: log the error
            return service_response(500, "Error creating family", "error", None)

    def family_belongs_to_user(self, family_id: int, user_id: int) -> bool:
        """
        Checks if a family belongs to a user.

        Args:
            family_id (int): The id of the family.
            user_id (int): The id of the user.

        Returns:
            bool: True if the family belongs to the user, False otherwise.
        """
        family = self.db.query(Family).filter_by(family_id=family_id, user_id=user_id).first()
        return family is not None

    def delete_family(self, family_id: int) -> Tuple[dict, int]:
        """
        Deletes a family.

        Args:
            family_id (int): The id of the family to delete.

        Returns:
            Tuple[dict, int]: A tuple containing a dictionary and HTTP status code.
        """
        try:
            family = self.db.query(Family).filter_by(family_id=family_id).first()
            if family:
                self.db.delete(family)
                self.db.commit()
                return service_response(200, "Family deleted successfully", "success", None)
            else:
                return service_response(404, "Family not found", "warning", None)
        except Exception:
            self.db.rollback()
            # Todo: log the error
            return service_response(500, "Error deleting family", "error", None)