from app.models import Link, Family, Event, Member
from app.extensions import db
from app.utils import auth_s
from app.family.services import FamilyService
from app.services.service_base import service_response
from typing import Tuple, Union, Optional
from http import HTTPStatus
from sqlalchemy.exc import SQLAlchemyError

class LinkService:

    def __init__(self, db_session=None):
        self.db = db_session or db.session
        self.family_service = FamilyService()

    def _check_existing_link(self, family_id: int) -> Optional[Link]:
        """Check if a link already exists for the given family."""
        return self.db.query(Link).filter_by(family_id=family_id).first()

    def create_link(self, entity: Union[Family, Event, Member]) -> Tuple[dict, int]:
        """
        Creates a new link for an entity.
        Args:
            entity: The entity (Family/Event/Member) to create a link for.
        Returns:
            Tuple[dict, int]: Response containing status and message.
        """
        try:
            existing_link = self._check_existing_link(entity.family_id)
            if existing_link:
                return service_response(
                    HTTPStatus.CONFLICT,
                    "Link already exists for this family",
                    "warning",
                    None
                )

            token = auth_s.dumps({"object_id": entity.family_id})
            new_link = Link(link=token, family_id=entity.family_id)

            self.db.add(new_link)
            self.db.commit()

            return service_response(
                HTTPStatus.CREATED,
                "Link created successfully",
                "success",
                new_link
            )
        except Exception:
            self.db.rollback()
            # Todo: log the error
            return service_response(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "Error creating link",
                "danger",
                None
            )

    def delete_link(self, link_id: int, family_id: int, user_id: int) -> Tuple[dict, int]:
        try:
            family_response = self.family_service.get_family_by_id(family_id, user_id)
            family_data, family_status_code = family_response
            print(family_response)
            if family_status_code == HTTPStatus.NOT_FOUND:
                return service_response(HTTPStatus.NOT_FOUND, "No Family found with this link", "warning", None)
            elif family_status_code == HTTPStatus.FORBIDDEN:
                return service_response(HTTPStatus.FORBIDDEN, "You do not have permission to delete this link", "danger", None)
            elif family_status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
                return family_response

            family = family_data.get("data")

            link = family.links[0] if family.links else None

            if not link:
                return service_response(HTTPStatus.NOT_FOUND, "Link not found", "warning", None)

            if link.link_id != link_id:
                return service_response(
                    HTTPStatus.FORBIDDEN,
                    "You do not have permission to delete this link",
                    "danger",
                    None
                )

            self.db.delete(link)
            self.db.commit()
            return service_response(HTTPStatus.OK, "Link deleted successfully", "success", None)
            
        except SQLAlchemyError:
            self.db.rollback()
            # logger.error(f"Database error while deleting link {link_id}: {str(e)}")
            return service_response(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "Database error occurred while deleting link",
                "danger",
                None
            )
        except Exception:
            self.db.rollback()
            # logger.error(f"Unexpected error while deleting link {link_id}: {str(e)}")
            return service_response(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "Unexpected error while deleting link",
                "danger",
                None
            )