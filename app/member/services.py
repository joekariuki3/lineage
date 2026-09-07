import traceback

from flask_login import current_user

from app.extensions import db
from app.family.services import FamilyService
from app.models import Member, Relationship
from app.services.service_base import service_response


class MemberService:
    """Service class for managing family members."""

    def __init__(self, db_session=None):
        self.db = db.session or db_session
        self.family_service = FamilyService()

    def get_member(self, member_id: int) -> tuple[dict, int]: #TODO: get multiple members by id in a list [id1, id2, id3] -> [member1, member2, member3]
        """
        Retrieve a member by its ID.

        This method queries the database to fetch a member with the specified
        ID. It validates access permissions for the current user to ensure
        that the member can be retrieved. If the member does not exist or if
        the user does not have permission to access it, appropriate error
        responses are returned. In case of an exception during the process,
        an internal server error response is returned.

        Arguments:
            member_id (int): The unique identifier of the member to retrieve.

        Returns:
            Tuple[dict, int]: A tuple containing a response dictionary with
            status, message, severity, data and the HTTP status code.
        """
        if not current_user or not current_user.is_authenticated:
            return service_response(401, "Unauthorized", "danger", None)
        try:
            member = self.db.query(Member).filter_by(member_id=member_id).first()

            if not member:
                return service_response(404, "Member not found", "warning", None)
            elif not MemberService.is_member_accessible_by_user(member):
                return service_response(403, "You do not have permission to access this member", "danger", None)
            return service_response(200, "Member retrieved successfully", "success", member)
        except Exception:
            # TODO: log error
            return service_response(500, "Error retrieving member", "danger", None)

    @staticmethod
    def is_member_accessible_by_user(member: Member) -> bool:
        """
        Checks if the current user has permission to access a member.

        Args:
            member (Member): The member to check.

        Returns:
            bool: True if the user has permission, False otherwise.
        """
        return member.family_id in [family.family_id for family in current_user.families]

    def create_member(self, **member_data) -> tuple[dict, int]:
        """
        Creates a new family member.

        Args:
            **member_data: A dictionary with member data.

        Returns:
            Tuple[dict, int]: A tuple containing a dictionary and HTTP status code.
        """
        try:
            new_member = Member(**member_data)
            self.db.add(new_member)
            self.db.commit()
            return service_response(201, "Member created successfully", "success", new_member)
        except ValueError as e:
            self.db.rollback()
            # TODO: log error
            print(f"Error creating member: {e!s}")
            error_message = traceback.format_exc()
            print(f"Traceback: {error_message}")
            return service_response(500, str(e), "danger", None)
        except Exception as e:
            self.db.rollback()
            # TODO: log error
            print(f"Error creating member: {e!s}")
            error_message = traceback.format_exc()
            print(f"Traceback: {error_message}")
            return service_response(500, "Error creating member", "danger", None)

    def create_root_member(self, **member_data):
        """
        Creates and adds a root member to a family in the database based on provided member data. It ensures that the
        family does not already have a root member and that the "root" attribute is set correctly. If the operation
        fails, the associated family is deleted, and the database transaction is rolled back.

        Parameters
        ----------
        **member_data: dict
            Keyword arguments representing member data, including family ID and root status.

        Returns
        -------
        dict
            A structured service response indicating the status of the operation, including an HTTP status code,
            message, category, and either the created member object or None.

        Raises
        ------
        Exception
            If the database transaction for creating a root member encounters any errors.

        Notes
        -----
        - The family must exist prior to creating its root member, as it ensures the presence of the family ID.
        - If a root member already exists in the family, the function will not create a new one and returns an
          appropriate service response instead.
        - Logs the error message upon exceptions and rollbacks the database session.
        """
        try:
            # confirm family was created successful member_data["family_id"] should not be none
            if "family_id" in member_data and member_data.get("family_id"):
                # also make sure the family does not have a root member already
                root_member = self.db.query(Member).filter_by(family_id=member_data.get("family_id"), root=True).first()
                if root_member:
                    return service_response(400, "Family already has a root member", "warning", None)

            # make sure the root value is true and if not set to true
            if "root" in member_data and  not member_data.get("root"):
                member_data["root"] = True

            root_member = Member(**member_data)
            self.db.add(root_member)
            self.db.commit()
            return service_response(201, "Root member created successfully", "success", root_member)
        except Exception as e:
            # delete created family since the root member was not created successfully
            response = self.family_service.delete_family(member_data.get("family_id"))
            family_data, status_code = response
            if status_code != 200:
                message, category = family_data.get("message"), family_data.get("category")
                return service_response(status_code, message, category, None)
            # TODO: log error
            print(f"Error creating root member: {e!s}")
            self.db.rollback()
            return service_response(500, "Error creating root member", "danger", None)

    def get_member_siblings(self, member_id: int) -> tuple[dict, int]:
        """
        Retrieves all siblings of a family member by their member ID.

        Args:
            member_id (int): The ID of the member.

        Returns:
            Tuple[dict, int]: A tuple containing a dictionary with the response message and
            the HTTP status code. If siblings are found, the dictionary will include the
            sibling data with a success message. If not found, it will contain an error message.
        """
        try:
            data, status = self.get_member(member_id)
            if status != 200:
                return data, status
            current_member = data.get('data')

            siblings = self.db.query(Member).where(
                Member.mother != "Null",
                Member.mother == current_member.mother,
                Member.father != "Null",
                Member.father == current_member.father,
                Member.member_id != current_member.member_id,
            ).order_by(Member.birthdate).all()

            if not siblings:
                return service_response(404, "No siblings found", "warning", None)
            return service_response(200, "Siblings retrieved successfully", "success", siblings)
        except Exception:
            # TODO: log error
            return service_response(500, "Error retrieving siblings", "danger", None)

    def get_member_children(self, member_id: int) -> tuple[dict, int]:
        """
        Retrieves all children of a family member by their member ID.

        Args:
            member_id (int): The ID of the member.

        Returns:
            Tuple[dict, int]: A tuple containing a dictionary with the response message and
            the HTTP status code. If children are found, the dictionary will include the
            child data with a success message. If not found, it will contain an error message.
        """
        try:
            data, status = self.get_member(member_id)
            if status != 200:
                return data, status
            current_member = data.get('data')

            children = self.db.query(Member).where(
                db.or_(
                Member.mother == current_member.member_id,
                Member.father == current_member.member_id
                )
            ).order_by(Member.birthdate).all()

            if not children:
                return service_response(404, "No children found", "warning", None)
            return service_response(200, "Children retrieved successfully", "success", children)
        except Exception:
            # TODO: log error
            return service_response(500, "Error retrieving children", "danger", None)

    def get_member_spouses(self, member_id: int) -> tuple[dict, int]:
        """
        Retrieves all spouses of a family member by their member ID.

        Args:
            member_id (int): The ID of the member.

        Returns:
            Tuple[dict, int]: A tuple containing a dictionary with the response message and
            the HTTP status code. If spouses are found, the dictionary will include the
            spouse data with a success message. If not found, it will contain an error message.
        """
        try:
            data, status = self.get_member(member_id)
            if status != 200:
                return data, status
            current_member = data.get('data')

            spouses_relationships = self.db.query(Relationship).where(
                db.or_(
                Relationship.member_id_1==current_member.member_id,
                Relationship.member_id_2==current_member.member_id,
                ),
                Relationship.relationship_type=='spouse'
                ).all()

            spouses = []
            for relationship in spouses_relationships:
                if relationship.member1 != current_member:
                    spouses.append(relationship.member1)
                else:
                    spouses.append(relationship.member2)

            if not spouses:
                return service_response(404, "No spouses found", "warning", None)
            return service_response(200, "Spouses retrieved successfully", "success", spouses)
        except Exception:
            # TODO: log error
            return service_response(500, "Error retrieving spouses", "danger", None)

    def update_member(self, member_id: int, **member_data) -> tuple[dict, int]:
        """
        Updates a family member's information.

        Args:
            member_id (int): The ID of the member to update.
            **member_data: A dictionary with updated member data.

        Returns:
            Tuple[dict, int]: A tuple containing a dictionary and HTTP status code.
        """
        try:
            data, status = self.get_member(member_id)
            if status != 200:
                return data, status
            member = data.get('data')

            for key, value in member_data.items():
                setattr(member, key, value)

            db.session.commit()
            return service_response(200, "Member updated successfully", "success", member)
        except Exception:
            self.db.rollback()
            # TODO: log error
            return service_response(500, "Error updating member", "danger", None)

    def delete_member(self,member_id: int) -> tuple[dict, int]:
        """
        Deletes a family member.

        Args:
            member_id (int): The ID of the member to delete.

        Returns:
            Tuple[dict, int]: A tuple containing a dictionary and HTTP status code.
        """
        try:
            data, status = self.get_member(member_id)
            if status != 200:
                return data, status
            member = data.get('data')

            self.db.delete(member)
            self.db.commit()
            return service_response(200, "Member deleted successfully", "success", None)
        except Exception:
            self.db.rollback()
            # TODO: log error
            return service_response(500, "Error deleting member", "danger", None)