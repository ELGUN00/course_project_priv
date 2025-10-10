from flask import Blueprint, request, jsonify,send_from_directory, abort, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from werkzeug.exceptions import BadRequest,HTTPException
from services.course_service import CourseService
from _logger import log
from models.user import Course
import os
from models.user import Course
from werkzeug.utils import secure_filename

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
        log("Girdi")
        user_id = get_jwt_identity()
        role = get_jwt().get('role')  # Assuming `request.user_role` is set somewhere based on JWT claim
        log(user_id)
        # Create an instance of CourseService
        course_service = CourseService(user_id, role)
        
        # Get data from the request
        data = request.get_json()
        log(data)
        # Add the course using the service
        course = course_service.create_course(data)
        # log(course.to_dict())
        # Return the course info
        return jsonify(course.to_dict()), 201
        
    except BadRequest as error:
        return jsonify({f"msg {data}": str(error)}), 400
    except Exception as error:
        return jsonify({"msg": f"{error}"}), 500


@course_bp.route('/modify/<int:course_id>', methods=['PUT'])
@jwt_required()
def modify_course(course_id):
    try:
        log('BURDA')
        # Get user info from JWT
        user_id = get_jwt_identity()
        log(user_id)
        role = get_jwt().get('role')   # Assuming `request.user_role` is set somewhere based on JWT claim
        
        log(role)
        
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
    
    
@course_bp.route('/<int:course_id>', methods=['GET'])
@jwt_required()
def get_the_course_by_id(course_id):
    try:
        log(course_id)
        course = CourseService.get_course(course_id=course_id)
        # Return the course info
        return jsonify(course), 200
    except HTTPException as http_error:
        # This captures `abort(404)` and similar HTTP aborts
        return jsonify({"msg": http_error.description}), http_error.code
    except BadRequest as error:
        return jsonify({"msg": str(error)}), 400
    except Exception as error:
        return jsonify({"msg": f"{error}"}), 500
    
    
@course_bp.route('/top-courses', methods=['GET'])
@jwt_required()
def get_top_courses_route():
    try:
        city = request.args.get('city')
        district = request.args.get('district')
        min_rating = float(request.args.get('min_rating', 0))
        online_str = request.args.get('online')
        online = None
        if online_str is not None:
            online = online_str.lower() in ['true', '1', 'yes']

        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))

        result = CourseService.get_top_courses(
            city=city,
            district=district,
            min_rating=min_rating,
            online=online,
            page=page,
            per_page=per_page
        )
        log(result)
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"msg": f"Unexpected error: {str(e)}"}), 500


@course_bp.route('/course-picture/<int:course_id>', methods=['GET'])
@jwt_required()
def get_course_picture(course_id):
    course = Course.query.get(course_id)
    if not course or not course.picture:
        return jsonify(None), 404
    
    filename = os.path.basename(course.picture)
    picture_dir = os.path.join(current_app.root_path, 'media', 'course_pictures')

    if not os.path.exists(os.path.join(picture_dir, filename)):
        return jsonify({"msg": f"File not found on server."}), 404

    return send_from_directory(picture_dir, filename)