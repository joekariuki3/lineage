
from app.extensions import db
from app.models import Member, Relationship
from app.services.service_base import service_response
from app.utils.constants import RelationType


class RelationshipService:
    """Service class for managing relationships between family members."""

    def __init__(self, db_session=None):
        self.db = db.session or db_session

    def create_relationship(self, member_id_1: int, member_id_2: int, relationship_type: RelationType) -> tuple[dict, int]:
        try:
            member1 = self.db.get(Member, member_id_1)
            member2 = self.db.get(Member, member_id_2)

            if not member1 or not member2:
                return service_response(404, "One or both members not found", "warning", None)

            new_relationship = Relationship(
                member_id_1=member_id_1,
                member_id_2=member_id_2,
                relationship_type=relationship_type
            )
            self.db.add(new_relationship)
            self.db.commit()
            return service_response(201, "Relationship created successfully", "success", new_relationship)
        except Exception as e:
            self.db.rollback()
            # TODO: log error
            print(f"Error creating relationship: {e!s}")
            return service_response(500, "Error creating relationship", "danger", None)