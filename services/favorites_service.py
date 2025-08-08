from models.user import User
from models.user import Favorites
from extensions import db

class FavoritesService:
    @staticmethod
    def add_favorite(user_id, course_id):
        try:
            # Check if the favorite already exists
            existing_favorite = Favorites.query.filter_by(user_id=user_id, course_id=course_id).first()
            if existing_favorite:
                return {'msg': 'Course already in favorites'}, 400
            
            # Add the favorite
            favorite = Favorites(user_id=user_id, course_id=course_id)
            db.session.add(favorite)
            db.session.commit()
            return {'msg': 'Course added to favorites'}, 201
        except Exception as e:
            db.session.rollback()
            return {'msg': f'Error adding favorite: {str(e)}'}, 500
    
    @staticmethod
    def get_favorites_for_user(user_id):
        try:
            # Fetch all favorites for the user
            favorites = Favorites.query.filter_by(user_id=user_id).order_by(Favorites.timestamp.desc()).all()
            favorite_data = [
                {
                    'id': fav.id,
                    'course_id': fav.course_id,
                    'timestamp': fav.timestamp,
                    'course': fav.course.to_dict()  # Ensure `Course` model has a `to_dict` method
                } for fav in favorites
            ]
            return {'favorites': favorite_data}, 200
        except Exception as e:
            return {'msg': f'Error retrieving favorites: {str(e)}'}, 500
    
    @staticmethod
    def delete_favorite(user_id, course_id):
        try:
            # Check if the favorite exists
            favorite = Favorites.query.filter_by(user_id=user_id, course_id=course_id).first()
            if not favorite:
                return {'msg': 'Favorite not found'}, 404
            
            # Delete the favorite
            db.session.delete(favorite)
            db.session.commit()
            return {'msg': 'Favorite removed successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'msg': f'Error deleting favorite: {str(e)}'}, 500
