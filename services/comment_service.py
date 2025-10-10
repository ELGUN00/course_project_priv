from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import get_jwt_identity
from models.user import User, Role, Comment, Course
from extensions import db
from flask import abort
from sqlalchemy import func
from sqlalchemy.orm import joinedload

class CommentService:
    
    @staticmethod
    def add_comment(course_id, user_id, content, rating):
        """Adds a comment to a course if the user is a student."""
        # Validate user
        user = User.query.get(user_id)
        if not user or user.role.value != "student":
            abort(403, description="Only students can add comments to courses.")
        
        # Validate course
        course = Course.query.get(course_id)
        if not course:
            abort(404, description="Course not found.")
        
        # Create the comment
        try:
            new_comment = Comment(
                content=content,
                rating=rating,
                user_id=user_id,
                course_id=course_id,
            )
            db.session.add(new_comment)
            db.session.commit()

            # Update course rating
            CommentService.update_course_rating(course_id)

            # After updating the course rating, also update the tutor's rating
            if course.tutor:
                CommentService.update_user_rating(course.tutor.id)
            if course.academy:
                CommentService.update_user_rating(course.academy.id)
            return new_comment
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, description=f"Failed to add comment: {str(e)}")
            # Update course rating
            CommentService.update_course_rating(course_id)

            # After updating the course rating, also update the tutor's rating
            if course.tutor:
                CommentService.update_user_rating(course.tutor.id)
            if course.academy:
                CommentService.update_user_rating(course.academy.id)
            return new_comment
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, description=f"Failed to add comment: {str(e)}")
    
    @staticmethod
    def modify_comment(comment_id, user_id, content=None, rating=None):
        """Modifies a comment if the user is its owner."""
        # Fetch comment
        comment = Comment.query.get(comment_id)
        if not comment or comment.user_id != user_id:
            abort(403, description="You are not allowed to modify this comment.")
        
        # Update content and rating
        if content:
            comment.content = content
        if rating is not None:  # If rating is provided, update it
            comment.rating = rating
        
        try:
            db.session.commit()

            # Update course rating after modifying the comment
            CommentService.update_course_rating(comment.course_id)

            # After updating the course rating, also update the tutor's rating
            if comment.course.tutor:
                CommentService.update_user_rating(comment.course.tutor.id)
            if comment.course.academy:
                CommentService.update_user_rating(comment.course.academy.id)
            return comment
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, description=f"Failed to modify comment: {str(e)}")

    @staticmethod
    def delete_comment(comment_id, user_id):
        """Deletes a comment if the user is its owner."""
        # Fetch comment
        comment = Comment.query.options(joinedload(Comment.course)).get(comment_id)
        if not comment or comment.user_id != user_id:
            raise ValueError("You are not allowed to delete this comment.")
        
        try:
            db.session.delete(comment)
            db.session.commit()

            # Update course rating after deleting the comment
            CommentService.update_course_rating(comment.course_id)

            # After updating the course rating, also update the tutor's rating
            if comment.course.tutor:
                CommentService.update_user_rating(comment.course.tutor.id)
            if comment.course.academy:
                CommentService.update_user_rating(comment.course.academy.id)

        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValueError(f"Failed to delete comment: {str(e)}")

    @staticmethod
    def update_course_rating(course_id):
        """Recalculates the course rating based on all its comments."""
        course = Course.query.get(course_id)
        if not course:
            raise ValueError("Course not found")

        # Calculate the average rating based on the comments' ratings
        average_rating = (
            db.session.query(func.avg(Comment.rating))
            .filter(Comment.course_id == course_id, Comment.rating.isnot(None))
            .scalar()
        )
        
        # Set the course's rating to the calculated average or 0 if no ratings exist
        course.rating = round(average_rating or 0, 0)
        
        # Commit the changes to the course
        db.session.commit()

    @staticmethod
    def update_user_rating(user_id):
        """Recalculates the user's rating based on the average of their courses' ratings."""
        user = User.query.get(user_id)
        if not user or user.role not in [Role.TUTOR, Role.ACADEMY]:
            raise ValueError("This method is only applicable for users with the role of tutor or academy.")
        
        # Determine the relationship to use based on the role
        if user.role == Role.TUTOR:
            courses = user.courses_as_tutor
        elif user.role == Role.ACADEMY:
            courses = user.courses_as_academy
        else:
            return 0

        # Join with comments and calculate the average rating
        average_rating = (
            db.session.query(func.avg(Course.rating))
            .filter(Course.id.in_([course.id for course in courses]))
            .scalar()
        )

        # Update the user's rating with the average of their courses' ratings
        user.rating = round(average_rating or 0, 0)
        db.session.commit()

