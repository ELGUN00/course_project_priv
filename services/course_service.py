from flask_jwt_extended import get_jwt_identity
from werkzeug.exceptions import BadRequest
from models.user import User, Role,Course, Comment
from extensions import db, es
from datetime import datetime
from sqlalchemy.orm import scoped_session
from flask import abort
import base64
from sqlalchemy import desc
from sqlalchemy.orm import joinedload
from flask import current_app
import uuid
import os

class CourseService:
    
    def __init__(self, user_id, role):
        self.user_id = user_id
        self.role = role

    def validate_course_data(self, data):
        # Check if necessary fields are present
        required_fields = ["title", "description", "price", "city", "district", "start_time", "end_time","online","picture"]
        for field in data:
            if field not in required_fields:
                raise BadRequest(f"'{field}' is required")
        
        # Validate start_time and end_time
        if 'start_time' in data and 'end_time' in data:
            if data['start_time'] >= data['end_time']:
                raise BadRequest("Start time must be before end time")

    def create_course(self, data):
        # Validate course data
        print('validate')
        self.validate_course_data(data)

        # Ensure the user has the right role
        if self.role not in ['tutor', 'academy']:
            raise BadRequest("Only tutors and academies can create courses.")

        # Create new course
        course = Course(
            title=data.get('title', None),  # Will be None if 'title' doesn't exist
            description=data.get('description', None),  # Default to None if 'description' is missing
            price=data.get('price', None),  # Default to None if 'price' is missing
            city=data.get('city', None),  # Default to None if 'city' is missing
            district=data.get('district', None),  # Default to None if 'district' is missing
            start_time=datetime.fromisoformat(data.get('start_time', None)) if data.get('start_time') else None,  # Convert start_time if exists, otherwise None
            end_time=datetime.fromisoformat(data.get('end_time', None)) if data.get('end_time') else None,  # Convert end_time if exists, otherwise None
            online=data.get('online', False),  # Default to False if 'online' is missing
            picture=self.save_course_picture(data.get('picture')),
            tutor_id=self.user_id if self.role == 'tutor' else None,  # Set tutor_id if the role is 'tutor'
            academy_id=self.user_id if self.role == 'academy' else None  # Set academy_id if the role is 'academy'
        )
        
        db.session.add(course)
        db.session.commit()
        course_data = {
            'title': course.title,
            'description': course.description,
        }
        try:
            es.index(index="courses", id=course.id, body=course_data)
        except Exception as e:
            raise ValueError("Error in indexinng course")
        return course

    def save_course_picture(self,base64_str):
        if not base64_str:
            return None

        # Generate a unique filename
        filename = f"course_{uuid.uuid4().hex}.jpg"
        filepath = os.path.join(current_app.root_path, 'media', 'course_pictures', filename)

        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # Decode base64 and write to file
        with open(filepath, 'wb') as f:
            f.write(base64.b64decode(base64_str))

        # Return relative path (to be stored in DB)
        return f"media/course_pictures/{filename}"

    def modify_course(self, course_id, data):
        # Validate course data
        self.validate_course_data(data)
        
        # Retrieve course
        course = Course.query.get(course_id)
        if not course:
            raise BadRequest("Course not found.")
        
        # Ensure the user is allowed to modify this course
        if (self.role == "tutor" and course.tutor_id != self.user_id) or (self.role == "academy" and course.academy_id != self.user_id):
            raise BadRequest("You are not authorized to modify this course.")

        # Update course fields if provided in the data
        course_updated = False  # Flag to check if the course is modified

        if 'title' in data:
            course.title = data['title']
            course_updated = True
        if 'description' in data:
            course.description = data['description']
            course_updated = True
        if 'price' in data:
            course.price = data['price']
        if 'city' in data:
            course.city = data['city']
        if 'district' in data:
            course.district = data['district']
        if 'start_time' in data:
            course.start_time = datetime.fromisoformat(data['start_time'])
        if 'end_time' in data:
            course.end_time = datetime.fromisoformat(data['end_time'])
        if 'online' in data:
            course.online = data['online']
        if 'picture' in data:
            course.picture = self.save_course_picture(data['picture'])

        # Commit changes to the database
        db.session.commit()

        # If course title or description was updated, also update it in Elasticsearch
        if course_updated:
            course_data = {
            'title': course.title,
            'description': course.description,
            }
            es.update(index="courses", id=course.id, body={"doc": course_data})   
        return course
    
    def get_all_comments_by_user_role(self, page=1, per_page=10):
        """
        Fetch all comments based on the user's role with pagination:
        - If the user is a student, return comments they wrote.
        - If the user is a tutor or academy, return comments for their courses.
        """
        if self.role == Role.STUDENT.value:
            # Return paginated comments written by the student
            comments = Comment.query.filter_by(user_id=self.user_id).order_by(Comment.created_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            comments_list = [comment.to_dict() for comment in comments]
            return {
                "total": comments.total,  # Total number of courses
                "page": comments.page,  # Current page
                "per_page": comments.per_page,  # Courses per page
                "total_pages": comments.pages,  # Total number of pages
                "comments": comments_list,  # List of courses for the current page
            }

        elif self.role in [Role.TUTOR.value, Role.ACADEMY.value]:
            # Fetch courses created by the tutor or academy
            courses = Course.query.filter(
                (Course.tutor_id == self.user_id) | (Course.academy_id == self.user_id)
            ).all()
            if not courses:
                return []

            # Fetch comments for these courses and paginate
            course_ids = [course.id for course in courses]
            comments = Comment.query.filter(Comment.course_id.in_(course_ids)).order_by(Comment.created_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            comments_list = [comment.to_dict() for comment in comments]
            return {
                "total": comments.total,  # Total number of courses
                "page": comments.page,  # Current page
                "per_page": comments.per_page,  # Courses per page
                "total_pages": comments.pages,  # Total number of pages
                "comments": comments_list,  # List of courses for the current page
            }

        else:
            raise ValueError("Invalid role")
    
    
    def get_comments_by_course(self,course_id, page, per_page):
        """Fetch paginated comments for a course."""
        # Check if course exists
        course = Course.query.get(course_id)
        if not course:
            abort(404, description="Comment for this course not found")
        
        paginated_comments = Comment.query.filter_by(course_id=course_id).order_by(Comment.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
        comments_list = [course.to_dict() for course in paginated_comments]
        # If no comments found
        return {
            "total": paginated_comments.total,  # Total number of courses
            "page": paginated_comments.page,  # Current page
            "per_page": paginated_comments.per_page,  # Courses per page
            "total_pages": paginated_comments.pages,  # Total number of pages
            "comments": comments_list,  # List of courses for the current page
        }
        
    def get_my_courses(self, page, per_page):
        if self.role == 'tutor':
            query = Course.query.filter_by(tutor_id=self.user_id).order_by(Course.timestamp.desc())
        elif self.role == 'academy':
            query = Course.query.filter_by(academy_id=self.user_id).order_by(Course.timestamp.desc())
        else:
            raise BadRequest("User role not authorized.")

        paginated_courses = query.paginate(page=page, per_page=per_page, error_out=False)
        courses_list = [course.to_dict(user_flag=False) for course in paginated_courses ]
        return {
            "total": paginated_courses.total,  # Total number of courses
            "page": paginated_courses.page,  # Current page
            "per_page": paginated_courses.per_page,  # Courses per page
            "total_pages": paginated_courses.pages,  # Total number of pages
            "courses": courses_list,  # List of courses for the current page
        }
    
    def delete_course(self, course_id):
        try:
            # Step 1: Retrieve the course by ID
            course = Course.query.get(course_id)
            if not course:
                raise BadRequest("Course not found.")
            
            # Step 2: Check if the user is authorized to delete the course
            if self.role == 'tutor' and course.tutor_id == self.user_id:
                # Delete all comments related to the course
                db.session.query(Comment).filter(Comment.course_id == course.id).delete(synchronize_session=False)
    
                # Step 3: Delete the course
                db.session.delete(course)
    
            elif self.role == 'academy' and course.academy_id == self.user_id:
                db.session.query(Comment).filter(Comment.course_id == course.id).delete(synchronize_session=False)
    
                # Step 3: Delete the course
                db.session.delete(course)
    
            else:
                raise BadRequest("You are not authorized to delete this course.")
            
            # Step 4: Commit in a controlled way (flush, then commit)
            # Ensure no other changes are pending before committing
            db.session.commit()
            es.delete(index="courses", id=course_id)
            
            return {"msg": "Course and associated comments deleted successfully."}
    
        except Exception as e:
            # In case of any error, rollback the transaction
            db.session.rollback()
            raise BadRequest(f"An error occurred: {str(e)}")
        
    @staticmethod
    def get_course_by_id(course_id):
        user = Course.query.get(course_id)
        if not user:
            return abort(404, description="Course with this id not found")
        return user
    
    @staticmethod
    def get_course(course_id):
        course = CourseService.get_course_by_id(course_id)
        return course.to_dict()
    
    @staticmethod
    def get_top_courses(city=None, district=None, min_rating=0, online=None, page=1, per_page=10):
        query = Course.query.options(
            joinedload(Course.tutor), joinedload(Course.academy)
        )

        # Filters
        if city:
            query = query.filter(Course.city.ilike(f"%{city}%"))
        if district:
            query = query.filter(Course.district.ilike(f"%{district}%"))
        if online is not None:
            query = query.filter(Course.online == online)
        if min_rating:
            query = query.filter(Course.rating >= min_rating)

        # Sort by rating
        query = query.order_by(desc(Course.rating))

        # Paginate
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)

        # Serialize
        courses = [course.to_dict(user_flag=True) for course in paginated.items]

        return {
            "courses": courses,
            "total": paginated.total,
            "page": paginated.page,
            "pages": paginated.pages,
            "per_page": paginated.per_page,
        }
