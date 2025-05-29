from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from werkzeug.exceptions import BadRequest
from services.course_service import CourseService

course_bp = Blueprint('course', __name__)

@course_bp.route('/courses/<int:user_id>', methods=['GET'])
@jwt_required()
def user_courses(user_id):
    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)  # Default to page 1
        per_page = request.args.get('per_page', 10, type=int)

        # Create an instance of CourseService
        course_service = CourseService(user_id=user_id)

        # Fetch courses for the given user ID
        courses = course_service.get_my_courses(page=page, per_page=per_page)

        # Return the course info
        return jsonify(courses), 200

    except BadRequest as error:
        return jsonify({"msg": str(error)}), 400
    except Exception as error:
        print(error)
        return jsonify({"msg": "Internal error"}), 500

@course_bp.route('/mycourses', methods=['GET'])
@jwt_required()
def mycourses():
    try:
        # Get user info from JWT
        user_id = get_jwt_identity()
        role = get_jwt().get('role')  # Assuming `request.user_role` is set somewhere based on JWT claim
        
        page = request.args.get('page', 1, type=int)  # Default to page 1 if not specified
        per_page = request.args.get('per_page', 10, type=int)
        # Create an instance of CourseService
        course_service = CourseService(user_id=user_id, role=role)
        
        courses = course_service.get_my_courses(page=page,per_page=per_page)
        
        # Return the course info
        return jsonify(courses), 200
        
    except BadRequest as error:
        return jsonify({"msg": str(error)}), 400
    except Exception as error:
        print(error)
        return jsonify({"msg": "Internal error"}), 500
    
@course_bp.route('/mycomments', methods=['GET'])
@jwt_required()
def get_all_comments_for_my_courses():
    try:
        # Get user info from JWT
        user_id = get_jwt_identity()
        role = get_jwt().get('role')  # Assuming `request.user_role` is set somewhere based on JWT claim
        if not user_id:
                return jsonify({"message": "User not found"}), 404

        page = request.args.get('page', 1, type=int)  # Default to page 1 if not specified
        per_page = request.args.get('per_page', 10, type=int)
        
        course_service = CourseService(user_id=user_id, role=role)
        
        comments = course_service.get_all_comments_by_user_role(page=page,per_page=per_page)
        # Return the course info
        return jsonify(comments), 200
        
    except BadRequest as error:
        return jsonify({"msg": str(error)}), 400
    except Exception as error:
        print(error)
        return jsonify({"msg": "Internal error"}), 500

@course_bp.route('/<int:course_id>', methods=['DELETE'])
@jwt_required()
def delete_course(course_id):
    try:
        # Get user info from JWT
        user_id = get_jwt_identity()
        role = get_jwt().get('role')  # Assuming `request.user_role` is set somewhere based on JWT claim
        
        # Create an instance of CourseService
        course_service = CourseService(user_id, role)
        
        message = course_service.delete_course(course_id)
        
        # Return the info
        return jsonify(message), 200
        
    except BadRequest as error:
        return jsonify({"msg": str(error)}), 400
    except Exception as error:
        print(error)
        return jsonify({"msg": "Internal error"}), 500

@course_bp.route('/comments/<int:course_id>', methods=['GET'])
@jwt_required()
def get_comments_by_course(course_id):
    try:
        # Get user info from JWT
        user_id = get_jwt_identity()
        role = get_jwt().get('role')  # Assuming `request.user_role` is set somewhere based on JWT claim
        
        # Create an instance of CourseService
        course_service = CourseService(user_id, role)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        comments = course_service.get_comments_by_course(course_id, page, per_page)
        return jsonify(comments), 200
        
    except BadRequest as error:
        return jsonify({"msg": str(error)}), 400
    except Exception as error:
        print(error)
        return jsonify({"msg": "Internal error"}), 500

@course_bp.route('/add-course', methods=['POST'])
@jwt_required()
def add_course():
    try: # Get user info from JWT
        print("Girdi")
        user_id = get_jwt_identity()
        role = get_jwt().get('role')  # Assuming `request.user_role` is set somewhere based on JWT claim
        print(user_id)
        # Create an instance of CourseService
        course_service = CourseService(user_id, role)
        
        # Get data from the request
        data = request.get_json()
        print(data)
        # Add the course using the service
        course = course_service.create_course(data)
        print(course.to_dict())
        # Return the course info
        return jsonify(course.to_dict()), 201
        
    except BadRequest as error:
        return jsonify({f"msg {data}": str(error)}), 400
    except Exception as error:
        print(error)
        return jsonify({"msg": "Internal error"}), 500


@course_bp.route('/modify/<int:course_id>', methods=['PUT'])
@jwt_required()
def modify_course(course_id):
    try:
        # Get user info from JWT
        user_id = get_jwt_identity()
        role = get_jwt().get('role')   # Assuming `request.user_role` is set somewhere based on JWT claim
        
        # Create an instance of CourseService
        course_service = CourseService(user_id, role)
        
        # Get data from the request
        data = request.get_json()
        
        # Modify the course using the service
        course = course_service.modify_course(course_id, data)
        
        # Return the updated course info
        return jsonify(course.to_dict()), 200
        
    except BadRequest as error:
        return jsonify({"msg": str(error)}), 400
    except Exception as error:
        print(error)
        return jsonify({"msg": "Internal error"}), 500
