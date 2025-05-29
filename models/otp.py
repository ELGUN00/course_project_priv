from extensions import db
from sqlalchemy.dialects.postgresql import BYTEA 
from sqlalchemy import Enum
from enum import Enum as PyEnum

# Defining roles as an Enum

class Otp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # email = db.Column(db.String(120), unique=True, nullable=False)
    otp = db.Column(db.String(4), nullable=True)
    otp_expiry = db.Column(db.DateTime, nullable=True)
    phone = db.Column(db.String(15), unique=True, nullable=True)


    def __init__(self, phone,otp,otp_expiry):
        self.phone = phone
        self.otp = otp
        self.otp_expiry = otp_expiry