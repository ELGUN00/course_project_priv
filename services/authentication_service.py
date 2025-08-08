import requests
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from models.user import User, Role
from extensions import db,es
import jwt
from werkzeug.exceptions import BadRequest
from datetime import datetime, timedelta
import base64
from _logger import log
class AuthService:
    def __init__(self, db_session=db.session):
        self.db = db_session

    def register_user(self, phone,data):
        phone = phone
        role = data.get("role")
        name = data.get("name")
        surname = data.get("surname")
        profile_picture = data.get("profile_picture",None)
        
        if not (phone):
            raise BadRequest("Phone is required.")
        if User.query.filter((User.phone == phone)).first():
            raise BadRequest("User with this phone already exists.")
        
        # Create user
        user = User(
            name=name,
            surname=surname,
            profile_picture= profile_picture,
            phone=phone, role=Role[role.upper()]
        )
        
        self.db.add(user)
        self.db.commit()
        #Save to elasticsearch
        resp = es.index(index="users", id=user.id, document={
            "user_id": user.id,
            "name": user.name,
            "surname": user.surname
        })
        additional_claims = {"role": user.role.value}
        token = create_access_token(identity=str(user.id), additional_claims=additional_claims,expires_delta = timedelta(days=180))
        res = {"access_token":'Bearer ' + token, "user": user.to_dict_profile()}
        return res

    def user_exists(self,phone):
        user = User.query.filter_by(phone=phone).first()
        return user is not None
    
    def login_user(self, phone):
        user = User.query.filter((User.phone == phone)).first()
        additional_claims = {"role": user.role.value}
        token = create_access_token(identity=str(user.id), additional_claims=additional_claims,expires_delta = timedelta(days=180))
        res = {"access_token":'Bearer ' + token, "user": user.to_dict_profile()}
        return res
    
    # def login(self, data):
    #     phone = data.get("phone")
    #     # Authenticate user
    #     user = User.query.filter((User.phone == phone)).first()
    #     # if not user or not user.check_password(password):
    #     #     raise BadRequest("Invalid credentials.")

    #     # Create JWT token
    #     additional_claims = {"role": user.role.value}
    #     token = create_access_token(identity=user.id, additional_claims=additional_claims)
    #     return {"access_token": 'Bearer ' + token, "user": user.to_dict()}
    
    
    def update_password(self, user_id, old_password, new_password):
        """Update the user's password if old password matches."""
        user = self.db.query(User).filter_by(id=user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Verify old password
        if not check_password_hash(user.password, old_password):
            return False

        # Update to the new password
        user.password = generate_password_hash(new_password)
        self.db.commit()
        return True
        
