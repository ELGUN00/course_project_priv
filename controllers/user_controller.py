from flask import Blueprint, request, jsonify
from services.user_service import UserService
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from werkzeug.exceptions import BadRequest
import base64 
from services.pageview_service import PageViewService
import os
from flask import send_from_directory, abort, current_app

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
        base64_image = data.get("profile_picture")
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

from _logger import log

@user_bp.route('/<int:viewed_user_id>', methods=['GET'])
@jwt_required()
def get_the_user_by_id(viewed_user_id):
    try:
        #viewed_user_id, viewer_user_id
        viewer_user_id = get_jwt_identity()
        user = UserService.get_profile(user_id=viewed_user_id)
        PageViewService.add_page_view(viewed_user_id, viewer_user_id)
        # Return the course info
        return jsonify(user), 200
    except BadRequest as error:
        return jsonify({"msg": str(error)}), 400
    except Exception as error:
        return jsonify({"msg": "Internal error"}), 500
    
@user_bp.route('/top-users', methods=['GET'])
@jwt_required()
def get_top_users_route():
    try:
        user_id = get_jwt_identity()

        role = request.args.get('role')
        location = request.args.get('location')
        degree = request.args.get('degree')
        min_rating = float(request.args.get('min_rating', 0))
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))

        result = UserService.get_top_users(
            user_id=user_id,
            role=role,
            location=location,
            degree=degree,
            min_rating=min_rating,
            page=page,
            per_page=per_page
        )

        return jsonify(result), 200

    except ValueError as ve:
        return jsonify({"msg": str(ve)}), 400
    except Exception as e:
        return jsonify({"msg": f"Unexpected error: {str(e)}"}), 500
    
@user_bp.route('/profile-picture/<int:user_id>', methods=['GET'])
@jwt_required()
def get_profile_picture(user_id):
    from services.user_service import UserService
    
    try:
        user = UserService.get_user_by_id(user_id)
        if not user.profile_picture:
            return jsonify(None), 404
        
        # Extract filename from stored path
        filename = os.path.basename(user.profile_picture)

        # Build absolute path to your media folder
        media_folder = os.path.join(current_app.root_path, 'media', 'profiles')

        # Optional: log info for debugging
        print(f"Serving profile picture: {filename} from {media_folder}")

        return send_from_directory(media_folder, filename)
    
    except Exception as e:
        return jsonify({"msg": f"Unexpected error: {str(e)}"}), 500