from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.comment_service import CommentService
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException

comment_bp = Blueprint('comment', __name__)

@comment_bp.route('/add', methods=['POST'])
@jwt_required()
def add_comment():
    """Add a new comment to a course."""
    try:
        data = request.get_json()
        course_id = data.get('course_id')
        content = data.get('content')
        rating = data.get('rating')
        
        # Validate input
        if not course_id or not content or not rating:
            return jsonify({"msg": "course_id, content, and rating are required"}), 400
        
        # Get user ID from JWT
        user_id = get_jwt_identity()

        # Delegate to service
        comment = CommentService.add_comment(course_id, user_id, content, rating)
        return jsonify(comment.to_dict()), 201
    except HTTPException as e:
        # Capture abort() calls and return JSON
        return jsonify({"msg": e.description}), e.code
    except SQLAlchemyError as e:
        return jsonify({"msg": f"Database msg: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"msg": f"Internal server msg: {str(e)}"}), 500

@comment_bp.route('/modify/<int:comment_id>', methods=['PUT'])
@jwt_required()
def modify_comment(comment_id):
    """Modify an existing comment."""
    try:
        data = request.get_json()
        content = data.get('content')
        rating = data.get('rating')
        
        # Get user ID from JWT
        user_id = get_jwt_identity()

        # Delegate to service
        comment = CommentService.modify_comment(comment_id, user_id, content, rating)
        return jsonify(comment.to_dict()), 200
    except HTTPException as e:
        # Capture abort() calls and return JSON
        return jsonify({"msg": e.description}), e.code
    except SQLAlchemyError as e:
        return jsonify({"msg": f"Database msg: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"msg": f"Internal server msg: {str(e)}"}), 500

@comment_bp.route('/delete/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    """Delete a comment."""
    try:
        # Get user ID from JWT
        user_id = get_jwt_identity()

        # Delegate to service
        CommentService.delete_comment(comment_id, user_id)
        return jsonify({"message": "Comment deleted successfully."}), 200
    
    except HTTPException as e:
        # Capture abort() calls and return JSON
        return jsonify({"msg": e.description}), e.code
    except SQLAlchemyError as e:
        return jsonify({"msg": f"Database msg: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"msg": f"Internal server msg: {str(e)}"}), 500
