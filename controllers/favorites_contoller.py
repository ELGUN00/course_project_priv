from flask import Blueprint, request
from services.favorites_service import FavoritesService
from flask_jwt_extended import jwt_required, get_jwt_identity

favorites_bp = Blueprint('favorites', __name__)

@favorites_bp.route('', methods=['POST'])
@jwt_required()
def add_favorite():
    data = request.json
    user_id = get_jwt_identity()

    # Extract IDs from request
    course_id = data.get('course_id')
    academy_id = data.get('academy_id')
    tutor_id = data.get('tutor_id')

    # Determine the target user (academy or tutor)
    target_user_id = academy_id or tutor_id

    if not course_id and not target_user_id:
        return {'msg': 'course_id or academy_id or tutor_id is required'}, 400

    return FavoritesService.add_favorite(
        user_id=user_id,
        course_id=course_id,
        target_user_id=target_user_id
    )

@favorites_bp.route('', methods=['GET'])
@jwt_required()
def get_favorites():
    user_id = get_jwt_identity()
    return FavoritesService.get_favorites_for_user(user_id)

@favorites_bp.route('', methods=['DELETE'])
@jwt_required()
def delete_favorite():
    data = request.json
    user_id = get_jwt_identity()

    # Extract IDs from request
    course_id = data.get('course_id')
    academy_id = data.get('academy_id')
    tutor_id = data.get('tutor_id')

    target_user_id = academy_id or tutor_id

    if not course_id and not target_user_id:
        return {'msg': 'course_id or academy_id or tutor_id is required'}, 400

    return FavoritesService.delete_favorite(
        user_id=user_id,
        course_id=course_id,
        target_user_id=target_user_id
    )
