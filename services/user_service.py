from models.user import User, Role
from extensions import db, es
import base64
from sqlalchemy import desc
from werkzeug.utils import secure_filename 
from models.user import User
import os 

MEDIA_FOLDER = '/media/profiles'
os.makedirs(MEDIA_FOLDER, exist_ok=True)

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
        return user.to_dict_profile()

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
        restricted_fields = {"phone", "rating", "role","profile_picture"}
    
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
        
        # Декодируем base64
        try:
            image_data = base64.b64decode(base64_image)
        except Exception:
            raise ValueError("Invalid base64 image data.")
        
        # Создаем имя файла, например user_45.jpg
        filename = secure_filename(f"user_{user_id}.jpg")
        file_path = os.path.join(MEDIA_FOLDER, filename)
        
        # Сохраняем файл
        with open(file_path, 'wb') as f:
            f.write(image_data)
        
        # Сохраняем путь к картинке в базе (относительный путь или полный)
        path = f"/media/profiles/{filename}"
        user.profile_picture = path
        db.session.commit()
        
        return {"msg": "Profile picture updated successfully.", "profile_picture": path}

    @staticmethod
    def delete_profile_picture(user_id):
        user = UserService.get_user_by_id(user_id)
        
        # Удаляем файл с диска, если существует
        if user.profile_picture:
            abs_path = os.path.join(os.getcwd(), user.profile_picture.lstrip('/'))
            if os.path.exists(abs_path):
                os.remove(abs_path)
        
        # Обнуляем путь в базе
        user.profile_picture = None
        db.session.commit()
        
        return {"msg": "Profile picture deleted successfully."}
    
    @staticmethod
    def get_top_users(role=None, location=None, degree=None, min_rating=0, page=1, per_page=10):
        query = User.query

        # Filter by role
        if role:
            role = role.upper()
            if role not in ['TUTOR', 'ACADEMY']:
                raise ValueError("Role must be 'TUTOR' or 'ACADEMY'")
            query = query.filter(User.role == Role[role])

        # Optional filters
        if location:
            query = query.filter(User.location.ilike(f"%{location}%"))
        if degree:
            query = query.filter(User.degree.ilike(f"%{degree}%"))
        if min_rating:
            query = query.filter(User.rating >= min_rating)

        # Sort by rating
        query = query.order_by(desc(User.rating))

        # Paginate
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)

        # Serialize
        users = [user.course_to_dict() for user in paginated.items]

        return {
            "users": users,
            "total": paginated.total,
            "page": paginated.page,
            "pages": paginated.pages,
            "per_page": paginated.per_page,
        }
