from sqlalchemy.orm import joinedload
from models.user import User, Course, Favorites  # Import your favorite model
from extensions import es, db
from _logger import log

class SearchService:
    @staticmethod
    def search_users(search_query: str, user_id=None, page=1, per_page=10, sort_by_rating=None, location=None):
        """
        Search for users by `name` or `username` in Elasticsearch.
        Returns users with an `is_favorite` field if user_id is provided.
        """
        try:
            if not search_query:
                raise ValueError("Search query cannot be empty")

            es_query = {
                "query": {
                    "bool": {
                        "should": [
                            {"match": {"name": search_query}},
                            {"match": {"surname": search_query}},
                            {"wildcard": {"name": {"value": f"*{search_query}*", "boost": 1.0}}},
                            {"wildcard": {"surname": {"value": f"*{search_query}*", "boost": 1.0}}}
                        ],
                        "minimum_should_match": 1
                    }
                },
                "sort": [{"_score": {"order": "desc"}}],
                "from": (page - 1) * per_page,
                "size": per_page
            }

            response = es.search(index="users", body=es_query)
            user_ids = [hit["_source"]["_id"] for hit in response['hits']['hits']]

            users_query = db.session.query(User)
            if user_ids:
                users_query = users_query.filter(User.id.in_(user_ids))

            if location:
                users_query = users_query.filter(User.location == location)

            if sort_by_rating:
                if sort_by_rating.lower() == "asc":
                    users_query = users_query.order_by(User.rating.asc())
                elif sort_by_rating.lower() == "desc":
                    users_query = users_query.order_by(User.rating.desc())

            total = users_query.count()
            users_query = users_query.limit(per_page).offset((page - 1) * per_page)
            users = users_query.all()

            # --- Favorites check ---
            favorite_user_ids = set()
            if user_id:
                favorites = db.session.query(Favorites).filter_by(user_id=user_id).all()
                favorite_user_ids = {fav.target_user_id for fav in favorites}
            
            result = []
            for u in users:
                data = u.to_dict()
                data["is_favorite"] = u.id in favorite_user_ids
                result.append(data)

            total_pages = (total + per_page - 1) // per_page
            return {
                "users": result,
                "total": total,
                "page": page,
                "per_page": per_page,
                "total_pages": total_pages
            }

        except ValueError as e:
            return {'msg': f'Error in elasticsearch: {str(e)}'}, 500

    @staticmethod
    def search_courses(search_query: str, user_id=None, page=1, per_page=10,
                       sort_by_price=None, sort_by_rating=None,
                       online=None, city=None, district=None,
                       start_time=None, end_time=None):
        """
        Search for courses by `title` or `description` in Elasticsearch with personalization.
        Adds `is_favorite` if user_id is provided.
        """
        try:
            if not search_query:
                raise ValueError("Search query cannot be empty")

            es_query = {
                "query": {
                    "bool": {
                        "should": [
                            {"match": {"title": search_query}},
                            {"match": {"description": search_query}},
                            {"wildcard": {"title": {"value": f"*{search_query}*", "boost": 1.0}}},
                            {"wildcard": {"description": {"value": f"*{search_query}*", "boost": 1.0}}}
                        ],
                        "minimum_should_match": 1,
                    }
                },
                "sort": [],
                "from": (page - 1) * per_page,
                "size": per_page
            }

            response = es.search(index="courses", body=es_query)
            course_ids = [hit["_id"] for hit in response['hits']['hits']]

            courses_query = db.session.query(Course).options(
                joinedload(Course.tutor), joinedload(Course.academy)
            )

            if course_ids:
                courses_query = courses_query.filter(Course.id.in_(course_ids))

            if city:
                courses_query = courses_query.filter(Course.city == city)
            if district:
                courses_query = courses_query.filter(Course.district == district)
            if start_time:
                courses_query = courses_query.filter(Course.start_time >= start_time)
            if end_time:
                courses_query = courses_query.filter(Course.end_time <= end_time)
            if online is not None:
                courses_query = courses_query.filter(Course.online == online)

            if sort_by_price:
                courses_query = courses_query.order_by(
                    Course.price.asc() if sort_by_price.lower() == 'asc' else Course.price.desc()
                )
            if sort_by_rating:
                courses_query = courses_query.order_by(
                    Course.rating.asc() if sort_by_rating.lower() == 'asc' else Course.rating.desc()
                )

            total = courses_query.count()
            courses_query = courses_query.limit(per_page).offset((page - 1) * per_page)
            courses = courses_query.all()

            # --- Favorites check ---
            favorite_course_ids = set()
            if user_id:
                favorites = db.session.query(Favorites).filter_by(user_id=user_id).all()
                favorite_course_ids = {fav.course_id for fav in favorites}

            result = []
            for c in courses:
                data = c.to_dict()
                data["is_favorite"] = c.id in favorite_course_ids
                result.append(data)

            total_pages = (total + per_page - 1) // per_page
            return {
                "courses": result,
                "total": total,
                "page": page,
                "per_page": per_page,
                "total_pages": total_pages
            }

        except ValueError as e:
            return {'msg': f'Error in elasticsearch: {str(e)}'}, 500
