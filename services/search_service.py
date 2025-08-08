from sqlalchemy.orm import sessionmaker
from models.user import User, Course  # Assuming the User model is imported
from extensions import es, db

class SearchService:
    @staticmethod
    def search_users(search_query: str, page=1, per_page=10, sort_by_rating=None, location=None):
        """
        Search for users by `name` or `username` in Elasticsearch.
        This method will return the user IDs and their corresponding details.
        
        :param search_query: Search string for name or username
        :return: List of user dictionaries with their full details
        """
        try:
            # Query Elasticsearch to find users by name or username
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
                "sort": [
                    {"_score": {"order": "desc"}}
                ],
                "from": (page - 1) * per_page,  # Pagination start index
                "size": per_page                # Number of results per page
            }

           

            response = es.search(index="users", body=es_query)

            # Extract user IDs from the search result
            user_ids = [hit["_source"]["_id"] for hit in response['hits']['hits']]

            # Fetch additional user data from the database using the user_ids
            users_query = db.session.query(User)
            
            if user_ids:
                users_query = users_query.filter(User.id.in_(user_ids))

            # Filter by location if provided
            if location:
                users_query = users_query.filter(User.location == location)

            # Sort by rating if specified
            if sort_by_rating:
                if sort_by_rating.lower() == "asc":
                    users_query = users_query.order_by(User.rating.asc())
                elif sort_by_rating.lower() == "desc":
                    users_query = users_query.order_by(User.rating.desc())

            # Apply pagination
            total = users_query.count()
            users_query = users_query.limit(per_page).offset((page - 1) * per_page)

            # Execute the query
            users = users_query.all()
            total_pages = (total + per_page - 1) // per_page  # Ceiling division

            # Prepare the response
            response = {
                "users": [user.to_dict() for user in users],  # User data
                "total": total,                              # Total number of users
                "page": page,                                # Current page
                "per_page": per_page,                        # Users per page
                "total_pages": total_pages                   # Total pages
            }
            return response
        except ValueError as e:
            return {'msg': f'Error in elasticsearch: {str(e)}'}, 500

    @staticmethod
    def search_courses(search_query: str, page=1, per_page=10, sort_by_price=None, sort_by_rating=None, online=None, city=None, district=None, start_time=None, end_time=None):
        """
        Search for courses by `title` or `description` in Elasticsearch with pagination, filtering, and sorting options.

        :param search_query: Search string for title or description
        :param page: Page number for pagination
        :param per_page: Number of results per page
        :param sort_by_price: Sort by price ('asc' or 'desc')
        :param sort_by_rating: Sort by rating ('asc' or 'desc')
        :param online: Filter by online status (True/False)
        :param city: Filter by city
        :param district: Filter by district
        :param start_time: Filter courses that start after this time
        :param end_time: Filter courses that end before this time
        :return: Dictionary with search results and pagination details
        """
        try:
            # Query Elasticsearch to find courses by title or description
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
                        "filter": []  # For additional filters (city, district, etc.)
                    }
                },
                "sort": [],
                "from": (page - 1) * per_page,
                "size": per_page
            }
            response = es.search(index="courses", body=es_query)
            
            # Extract user IDs from the search result
            courses_ids = [hit["_id"] for hit in response['hits']['hits']]

            # Fetch additional user data from the database using the user_ids
            courses_query = db.session.query(Course)
            
            if courses_ids:
                courses_query = courses_query.filter(Course.id.in_(courses_ids))
            # Apply filters if provided
            if city:
                courses_query = courses_query.filter(Course.city == city)

            # Apply district filter if provided
            if district:
                courses_query = courses_query.filter(Course.district == district)

            # Apply start_time filter if provided (greater than or equal)
            if start_time:
                courses_query = courses_query.filter(Course.start_time >= start_time)

            # Apply end_time filter if provided (less than or equal)
            if end_time:
                courses_query = courses_query.filter(Course.end_time <= end_time)

            # Apply online filter if provided (True or False)
            if online is not None:
                courses_query = courses_query.filter(Course.online == online)

            # Sorting by price if specified
            if sort_by_price:
                if sort_by_price.lower() == 'asc':
                    courses_query = courses_query.order_by(Course.price.asc())
                elif sort_by_price.lower() == 'desc':
                    courses_query = courses_query.order_by(Course.price.desc())

            # Sorting by rating if specified
            if sort_by_rating:
                if sort_by_rating.lower() == 'asc':
                    courses_query = courses_query.order_by(Course.rating.asc())
                elif sort_by_rating.lower() == 'desc':
                    courses_query = courses_query.order_by(Course.rating.desc())

            # Pagination (apply the limit and offset)
            total = courses_query.count()
            courses_query = courses_query.limit(per_page).offset((page - 1) * per_page)

            # Execute the query and get the results
            courses = courses_query.all()
            total_pages = (total + per_page - 1) // per_page  # Ceiling division for total pages

            # Prepare the response
            response = {
                "courses": [course.to_dict() for course in courses],  # Return course data as dictionaries
                "total": total,                                      # Total number of courses
                "page": page,                                        # Current page
                "per_page": per_page,                                # Number of courses per page
                "total_pages": total_pages                           # Total number of pages
            }
            return response

        except ValueError as e:
            return {'msg': f'Error in elasticsearch: {str(e)}'}, 500