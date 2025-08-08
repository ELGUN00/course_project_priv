from flask import Blueprint, request, jsonify
from services.user_service import UserService
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from services.search_service import SearchService

search_bp = Blueprint("search", __name__)

@search_bp.route('/users/', methods=['GET'])
@jwt_required()
def get_user_profiles():
    try:
        # Extract query parameters
        query = request.args.get("query", None)
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        sort_by_rating = request.args.get("sort_by_rating", None)  # "asc" or "desc"
        location = request.args.get("location", None)

        # Call the search service with the extracted parameters
        users = SearchService.search_users(
            search_query=query,
            page=page,
            per_page=per_page,
            sort_by_rating=sort_by_rating,
            location=location
        )

        if not users:
            return jsonify({"msg": "No users found"}), 404

        return jsonify(users), 200
    except ValueError as e:
        return jsonify({"msg": str(e)}), 400
    except Exception as e:
        return jsonify({"msg": f"Server error: {str(e)}"}), 500

@search_bp.route('/courses/', methods=['GET'])
@jwt_required()
def get_courses():
    try:
        # Extract query parameters
        query = request.args.get("query", None)
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        sort_by_price = request.args.get("sort_by_price", None)  # "asc" or "desc"
        sort_by_rating = request.args.get("sort_by_rating", None)  # "asc" or "desc"
        online = request.args.get("online", None)  # 'True' or 'False'
        city = request.args.get("city", None)
        district = request.args.get("district", None)
        start_time = request.args.get("start_time", None)
        end_time = request.args.get("end_time", None)

        # Call the search service with the extracted parameters
        courses = SearchService.search_courses(
            search_query=query,
            page=page,
            per_page=per_page,
            sort_by_price=sort_by_price,
            sort_by_rating=sort_by_rating,
            online=online,
            city=city,
            district=district,
            start_time=start_time,
            end_time=end_time
        )

        if not courses:
            return jsonify({"msg": "No courses found"}), 404

        return jsonify(courses), 200

    except ValueError as e:
        return jsonify({"msg": str(e)}), 400
    except Exception as e:
        return jsonify({"msg": f"Server error: {str(e)}"}), 500


