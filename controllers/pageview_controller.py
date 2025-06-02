from flask import Blueprint, request, jsonify
from services.pageview_service import PageViewService
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt


page_view_bp = Blueprint('page_view', __name__)


# @page_view_bp.route('', methods=['POST'])
# @jwt_required()
# def add_page_view():
#     data = request.json
#     viewed_user_id = data.get('viewed_user_id')
#     viewer_user_id = get_jwt_identity()

#     if not viewed_user_id or not viewer_user_id:
#         return jsonify({'msg': 'Both viewed_user_id and viewer_user_id are required'}), 400

#     return PageViewService.add_page_view(viewed_user_id, viewer_user_id)


@page_view_bp.route('/count', methods=['GET'])
@jwt_required()
def get_views_for_user():
    user_id = get_jwt_identity()
    return PageViewService.get_views_count_for_user(user_id)


@page_view_bp.route('', methods=['GET'])
@jwt_required()
def get_views_count_for_user():
        """
        Get paginated and filtered views for a user.
        """
        try:
            user_id = get_jwt_identity()
            # Parse query parameters
            page = int(request.args.get('page', 1))  # Default page is 1
            page_size = int(request.args.get('page_size', 10))  # Default page size is 10
            start_timestamp = request.args.get('start_timestamp', None)
            end_timestamp = request.args.get('end_timestamp', None)

            # Call service function
            result, status = PageViewService.get_views_for_user(
                user_id=user_id,
                page=page,
                page_size=page_size,
                start_timestamp=start_timestamp,
                end_timestamp=end_timestamp
            )
            return result, status
        except ValueError as e:
            return {'msg': f'Invalid input: {str(e)}'}, 400
        except Exception as e:
            return {'msg': f'Error processing request: {str(e)}'}, 500