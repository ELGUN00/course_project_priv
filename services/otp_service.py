# import random
# import firebase_admin
# from firebase_admin import credentials, auth
from models.otp import Otp
from extensions import db
from datetime import timedelta, datetime
from flask_jwt_extended import create_access_token
from werkzeug.exceptions import BadRequest

class OTPService:
    def __init__(self, db_session=db.session):
        self.db = db_session
        
    def generate_otp(self):
        # return str(random.randint(1000, 9999))
        return str('1111')

    def send_otp(self, phone, otp):
        # Integrate with Twilio, AWS SNS, or Email APIs
        # if "@" in email_or_phone:
        #     # Send OTP via email
        #     pass
        # else:
        print(f'Send OTP to {phone} OTP code: {otp}')
    
    def set_otp(self, phone, otp,otp_expiry):
        otp_record = db.session.query(Otp).filter(Otp.phone == phone).first()
        if otp_record:
            otp_record.otp = otp
            otp_record.otp_expiry = otp_expiry
            db.session.commit()
            return create_access_token(identity=phone, expires_delta=timedelta(minutes=2))
        else:
            new_otp_record = Otp(phone=phone, otp=otp, otp_expiry=otp_expiry)
            db.session.add(new_otp_record)
            db.session.commit()
            return create_access_token(identity=phone, expires_delta=timedelta(minutes=2))

    def verify_otp(self, phone, otp):
        otp_record = db.session.query(Otp).filter(Otp.phone == phone).first()
        if not otp_record or otp_record.otp != otp or otp_record.otp_expiry < datetime.utcnow():
            raise BadRequest("Invalid or expired OTP.")
        otp_record.otp = None
        otp_record.otp_expiry = None
        db.session.commit()
        return True

            
