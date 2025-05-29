from extensions import db
from sqlalchemy.dialects.postgresql import BYTEA 
from sqlalchemy import Enum
from enum import Enum as PyEnum
import base64
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import func
from sqlalchemy import event
from sqlalchemy.ext.hybrid import hybrid_property


# Defining roles as an Enum
class Role(PyEnum):
    STUDENT = "student"
    ACADEMY = "academy"
    TUTOR = "tutor"

class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    surname = db.Column(db.String(50))
    profile_picture = db.Column(BYTEA, nullable=True) 
    phone = db.Column(db.String(15), unique=True, nullable=True)
    rating = db.Column(db.Float, default=0)  # Average rating (if applicable)
    bio = db.Column(db.Text, nullable=True)
    degree = db.Column(db.String(150), nullable=True)
    location = db.Column(db.String(50),nullable=True)
    role = db.Column(Enum(Role,name="role"), nullable=False, default=Role.STUDENT)

    # Relationships
    comments = db.relationship('Comment', back_populates='user', lazy='dynamic')
    courses_as_tutor = db.relationship('Course', back_populates='tutor', foreign_keys='Course.tutor_id', lazy='dynamic')
    courses_as_academy = db.relationship('Course', back_populates='academy', foreign_keys='Course.academy_id', lazy='dynamic')
    
    views_received = db.relationship('PageView', foreign_keys='PageView.viewed_user_id', back_populates='viewed_user', lazy='dynamic')
    views_made = db.relationship('PageView', foreign_keys='PageView.viewer_user_id', back_populates='viewer_user', lazy='dynamic')
    
    favorites = db.relationship('Favorites', back_populates='user', lazy='dynamic')
    
    def __init__(self, name, surname, role=Role.STUDENT, phone=None, profile_picture=None, 
                 bio=None, degree=None, location=None, rating=0):
        self.name = name
        self.surname = surname
        self.role = role
        self.phone = phone
        self.profile_picture = profile_picture or None
        self.bio = bio
        self.degree = degree
        self.location = location
        self.rating = rating
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "surname": self.surname,
            "role": self.role.value,
            "phone": self.phone,
            "profile_picture": base64.b64encode(self.profile_picture).decode('utf-8') if self.profile_picture else None,
            "rating": self.rating,
            "bio": self.bio,
            "degree": self.degree,
            "location": self.location,
        }
        
    def course_to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "surname": self.surname,
            "role": self.role.value,
            "rating":self.rating,
            "phone": self.phone,
            "profile_picture": base64.b64encode(self.profile_picture).decode('utf-8') if self.profile_picture else None,
        }
    
class Course(db.Model):
    __tablename__ = 'course'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
     # Average rating (calculated from CourseRating)
    tutor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Linked to a Tutor (User with role "tutor")
    academy_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Optional link to Academy (User with role "academy")
    city = db.Column(db.String(100), nullable=False)
    district = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    price = db.Column(db.Float, nullable=False)
    rating = db.Column(db.Float, default=0)
    online = db.Column(db.Boolean, default=False)  # Online/offline course indicator
    picture = db.Column(BYTEA, nullable=True)   # URL or file path to the course picture
    timestamp = db.Column(db.DateTime, default=func.now())  # Timestamp for the view
    # Relationships
    comments = db.relationship('Comment', back_populates='course', lazy='dynamic')
    tutor = db.relationship('User', back_populates='courses_as_tutor', foreign_keys=[tutor_id])
    academy = db.relationship('User', back_populates='courses_as_academy', foreign_keys=[academy_id])

    favorites = db.relationship('Favorites', back_populates='course', lazy='dynamic')
    
    def to_dict(self,user_flag=True):
        course_dict = {
            "id":self.id,
            "title": self.title,
            "description": self.description,
            "rating": self.rating,
            "tutor": self.tutor_id,
            "academy": self.academy_id,
            "city": self.city,
            "district": self.district,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "price": self.price,
            "online": self.online,  # Add the new field
            "picture": base64.b64encode(self.picture).decode('utf-8') if self.picture else None,
        }
        
        if user_flag:
            if self.academy:
                course_dict["academy"] = self.academy.course_to_dict()

            if self.tutor:
                course_dict["tutor"] = self.tutor.course_to_dict()
            
        return course_dict
    
    
     
        
class Comment(db.Model):
    __tablename__ = 'comment'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=True)
    rating = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Linked to User (Student/Tutor/Academy)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=True)  # Linked to a Course
    
    user = db.relationship('User', back_populates='comments')
    course = db.relationship('Course', back_populates='comments')

    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "rating": self.rating,
            "created_at": self.created_at,
            "user": self.user.to_dict(),
            "course": self.course.title,
            "course_id": self.course.id
        }
        

class PageView(db.Model):
    __tablename__ = 'page_view'
    
    id = db.Column(db.Integer, primary_key=True)
    viewed_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # User whose page is being viewed
    viewer_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # User who is viewing the page
    timestamp = db.Column(db.DateTime, default=func.now())  # Timestamp for the view
    
    # Relationships
    viewed_user = db.relationship('User', foreign_keys=[viewed_user_id], back_populates='views_received')
    viewer_user = db.relationship('User', foreign_keys=[viewer_user_id], back_populates='views_made')

class Favorites(db.Model):
    __tablename__ = 'favorites'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)  # User whose page is being viewed
    course_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # User who is viewing the page
    timestamp = db.Column(db.DateTime, default=func.now())  # Timestamp for the view
    
    # Relationships
    user = db.relationship('User', back_populates='favorites')
    course = db.relationship('Course', back_populates='favorites')