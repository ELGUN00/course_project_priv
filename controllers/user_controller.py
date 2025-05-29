from flask import Blueprint, request, jsonify
from services.user_service import UserService
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
import base64 
user_bp = Blueprint("user", __name__)

@user_bp.route('/', methods=['GET'])
@jwt_required()
def get_user_profile():
    try:
        user_id = get_jwt_identity()
        profile = UserService.get_profile(user_id)
        return jsonify(profile), 200
    except ValueError as e:
        return jsonify({"msg": str(e)}), 404

@user_bp.route('/', methods=['PUT'])
@jwt_required()
def update_user_profile():
    try:
        user_id = get_jwt_identity()
        update_data = request.json  # Expects a JSON object
        updated_profile = UserService.update_user(user_id, update_data)
        return jsonify(updated_profile), 200
    except ValueError as e:
        return jsonify({"msg": str(e)}), 404

@user_bp.route('/profile-picture', methods=['PUT'])
@jwt_required()
def set_profile_picture():
    try:
        user_id = get_jwt_identity()
        data = request.json
        base64_image = base64.b64decode(data.get("profile_picture"))
        response = UserService.set_profile_picture(user_id, base64_image)
        return jsonify(response), 200
    except ValueError as e:
        return jsonify({"msg": str(e)}), 400

@user_bp.route('/profile-picture', methods=['DELETE'])
@jwt_required()
def delete_profile_picture():
    try:
        user_id = get_jwt_identity()
        response = UserService.delete_profile_picture(user_id)
        return jsonify(response), 200
    except ValueError as e:
        return jsonify({"msg": str(e)}), 404
