from flask import Blueprint, request
from services.favorites_service import FavoritesService
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

favorites_bp = Blueprint('favorites', __name__)

@favorites_bp.route('', methods=['POST'])
@jwt_required()
def add_favorite():
    data = request.json
    user_id = get_jwt_identity()
    course_id = data.get('course_id')
    if not user_id or not course_id:
        return {'msg': 'user_id and course_id are required'}, 400
    return FavoritesService.add_favorite(user_id, course_id)

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
    course_id = data.get('course_id')
    if not user_id or not course_id:
        return {'msg': 'user_id and course_id are required'}, 400
    return FavoritesService.delete_favorite(user_id, course_id)
