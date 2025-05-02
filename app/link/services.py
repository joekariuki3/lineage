from app.models import Link, Family, Event, Member
from app.extensions import db
from app.utils import auth_s
from app.family.services import FamilyService
from app.services.service_base import service_response
from flask_login import current_user
from typing import Tuple, Union

class LinkService:
    @staticmethod
    def create_link(object: Union[Family, Event, Member] ) -> Tuple[dict, int]:
        """
        Creates a new link for an object.

        Args:
            object (object): The object to create a link for.

        Returns:
            Tuple[dict, int]: A tuple containing a dictionary and HTTP status code.
        """
        try:
            existing_link = db.session.query(Link).filter_by(family_id=object.family_id).first()
            if existing_link:
                return service_response(409, "Link already exists", "warning", None)

            token = auth_s.dumps({"object_id": object.family_id})

            new_link = Link(link=token, family_id=object.family_id)
            db.session.add(new_link)
            db.session.commit()
            return service_response(201, "Link created successfully", "success", new_link)
        except Exception as e:
            db.session.rollback()
            # Todo: log the error
            return service_response(500, "Something went wrong", "danger", None)

    @staticmethod
    def delete_link(link_id: int) -> Tuple[dict, int]:
        """
        Deletes a link.

        Args:
            link_id (int): The id of the link to delete.

        Returns:
            Tuple[dict, int]: A tuple containing a dictionary and HTTP status code.
        """
        try:
            link = db.session.query(Link).filter_by(link_id=link_id).first()
            if not link:
                return service_response(404, "Link not found", "warning", None)

            if not FamilyService.family_belongs_to_user(family_id=link.family_id, user_id=current_user.user_id):
                return service_response(403, "You do not have permission to delete this link", "danger", None)

            db.session.delete(link)
            db.session.commit()
            return service_response(200, "Link deleted successfully", "success", None)
        except Exception as e:
            db.session.rollback()
            # Todo: log the error
            return service_response(500, "Something went wrong", "danger", None)