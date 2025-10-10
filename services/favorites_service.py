from models.user import User
from models.user import Favorites
from extensions import db

class FavoritesService:
    @staticmethod
    def add_favorite(user_id, course_id=None, target_user_id=None):
        if not course_id and not target_user_id:
            return {'msg': 'Either course_id or target_user_id is required'}, 400

        # Check if favorite already exists
        existing_favorite = Favorites.query.filter_by(
            user_id=user_id,
            course_id=course_id,
            target_user_id=target_user_id
        ).first()
        if existing_favorite:
            return {'msg': 'Already in favorites'}, 400

        # Create favorite
        favorite = Favorites(
            user_id=user_id,
            course_id=course_id,
            target_user_id=target_user_id
        )
        try:
            db.session.add(favorite)
            db.session.commit()
            return {'msg': 'Added to favorites'}, 201
        except Exception as e:
            db.session.rollback()
            return {'msg': f'Error adding favorite: {str(e)}'}, 500

    @staticmethod
    def get_favorites_for_user(user_id):
        favorites = Favorites.query.filter_by(user_id=user_id).order_by(Favorites.timestamp.desc()).all()
        favorite_data = []

        for fav in favorites:
            data = {
                'id': fav.id,
                'timestamp': fav.timestamp
            }
            if fav.course_id:
                data['type'] = 'course'
                data['course'] = fav.course.to_dict()
            elif fav.target_user_id:
                data['type'] = fav.target_user.role.value  # "TUTOR" or "ACADEMY"
                data['user'] = fav.target_user.to_dict()
            favorite_data.append(data)

        return {'favorites': favorite_data}, 200

    @staticmethod
    def delete_favorite(user_id, course_id=None, target_user_id=None):
        favorite = Favorites.query.filter_by(
            user_id=user_id,
            course_id=course_id,
            target_user_id=target_user_id
        ).first()

        if not favorite:
            return {'msg': 'Favorite not found'}, 404

        try:
            db.session.delete(favorite)
            db.session.commit()
            return {'msg': 'Favorite removed successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'msg': f'Error deleting favorite: {str(e)}'}, 500
