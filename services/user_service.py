from models.user import User
from extensions import db, es
import base64 

class UserService:
    @staticmethod
    def get_user_by_id(user_id):
        user = User.query.get(user_id)
        if not user:
            raise ValueError(f"User with id {user_id} not found.")
        return user

    @staticmethod
    def get_profile(user_id):
        user = UserService.get_user_by_id(user_id)
        return user.to_dict()

    @staticmethod
    def update_user(user_id, update_data):
        """
        Update a user with the provided data, while validating keys and restricting updates to certain fields.
        
        :param user_id: ID of the user to update
        :param update_data: Dictionary containing the fields to update
        :raises ValueError: If invalid fields or restricted fields are provided
        :return: Updated user as a dictionary
        """
        # Restricted fields that cannot be updated
        restricted_fields = {"phone", "rating", "role"}
    
        # Fetch the user from the database
        user = UserService.get_user_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
    
        # Get all valid attributes of the User model
        valid_fields = {column.name for column in User.__table__.columns}
    
        # Validate update_data keys
        for field in update_data:
            if field not in valid_fields:
                raise ValueError(f"Invalid field: {field}")
            if field in restricted_fields:
                raise ValueError(f"Cannot update restricted field: {field}")
    
        # Update allowed fields
        for field, value in update_data.items():
            if hasattr(user, field):
                setattr(user, field, value)
    
        # Commit changes to the database
        db.session.commit()

        if "name" in update_data or "surname" in update_data:
            es_update_data = {}
            if "name" in update_data:
                es_update_data["name"] = update_data["name"]
            if "surname" in update_data:
                es_update_data["surname"] = update_data["surname"]
            
            # Update user in Elasticsearch
            es.index(index="users", id=user_id, document=es_update_data)
        
        # Return updated user as a dictionary
        return user.to_dict()

    @staticmethod
    def set_profile_picture(user_id, base64_image):
        user = UserService.get_user_by_id(user_id)
        
        if not base64_image:
            raise ValueError("Base64 image data is required.")
        
        # Decode base64 and store as bytes
        user.profile_picture = base64_image
        db.session.commit()
        return {"msg": "Profile picture updated successfully."}

    @staticmethod
    def delete_profile_picture(user_id):
        user = UserService.get_user_by_id(user_id)
        user.profile_picture = None
        db.session.commit()
        return {"msg": "Profile picture deleted successfully."}
