from models.user import User
from models.user import PageView
from extensions import db

class PageViewService:
    @staticmethod
    def add_page_view(viewed_user_id, viewer_user_id):
        try:
            # Check if both users exist
            viewed_user = User.query.get(viewed_user_id)
            viewer_user = User.query.get(viewer_user_id)
            if not viewed_user or not viewer_user:
                return {'msg': 'User not found'}, 404

            # Add the page view
            page_view = PageView(viewed_user_id=viewed_user_id, viewer_user_id=viewer_user_id)
            db.session.add(page_view)
            db.session.commit()
            return {'msg': 'Page view added successfully'}, 201
        except ValueError as e:
            db.session.rollback()
            return {'msg': f'Error adding page view: {str(e)}'}, 500

    @staticmethod
    def get_views_count_for_user(user_id):
        try:
            # Fetch all views for the specified user
            views = PageView.query.filter_by(viewed_user_id=user_id).all()
            if not views:
                return {'msg': 'No views found for this user'}, 404

            # Serialize the views
            views_count = len(views)
            return {'count': views_count}, 200
        except ValueError as e:
            return {'msg': f'Error retrieving views: {str(e)}'}, 500
    
    @staticmethod
    def get_views_for_user(user_id, page=1, page_size=10, start_timestamp=None, end_timestamp=None):
        try:
            # Build the base query
            query = PageView.query.filter_by(viewed_user_id=user_id)

            # Add timestamp filtering if specified
            if start_timestamp and end_timestamp:
                query = query.filter(PageView.timestamp.between(start_timestamp, end_timestamp))

            # Count total views
            total_views = query.count()

            # Apply pagination
            views = query.offset((page - 1) * page_size).limit(page_size).all()

            # Serialize the views
            view_data = [
                {
                    'viewer_user': view.viewer_user.to_dict(),
                    'timestamp': view.timestamp
                } for view in views
            ]

            return {
                'views': view_data,
                'views_count': total_views,
                'page': page,
                'page_size': page_size,
                'total_pages': (total_views + page_size - 1) // page_size  # Calculate total pages
            }, 200
        except Exception as e:
            return {'msg': f'Error retrieving views: {str(e)}'}, 500