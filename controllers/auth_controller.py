from flask import jsonify, request,Blueprint
from services.authentication_service import AuthService
from services.otp_service import OTPService
from utils.validators import validate_registration
from werkzeug.exceptions import BadRequest
from datetime import datetime, timedelta
from flask_jwt_extended import jwt_required,  get_jwt_identity, create_access_token


auth_bp = Blueprint("auth", __name__)
auth_service = AuthService()
otp_service = OTPService()


@auth_bp.errorhandler(ValueError)
@auth_bp.route('/register', methods=['POST'])
@jwt_required()
def register():
    try:
        data = request.get_json()
        validate_registration(data)
        phone = get_jwt_identity()
        user = auth_service.register_user(phone,data)
        return jsonify(user), 201
    except  BadRequest as error:
        response = {
        "msg": str(error)
        }
        return jsonify(response), 400
    except Exception as error:
        print(error)
        response = {
        "msg": "Internal problem"
        }
        return jsonify(response), 404 

@auth_bp.errorhandler(ValueError)
@auth_bp.route('/send-otp', methods=['POST'])
def send_otp():
    try:
        data = request.get_json()
        otp = otp_service.generate_otp()
        otp_service.send_otp(data.get("phone"), otp)
        otp_expiry =datetime.utcnow() + timedelta(minutes=3),
        token = otp_service.set_otp(data.get("phone"), otp,otp_expiry)
        return jsonify({"message": 'OTP is sended',"access_token":'Bearer ' + token}), 201
    except  BadRequest as error:
        response = {
        "msg": str(error)
        }
        return jsonify(response), 400
    except Exception as error:
        print(error)
        response = {
        "msg": "Internal problem"
        }
        return jsonify(response), 500 

@auth_bp.errorhandler(ValueError)            
@auth_bp.route("/verify-otp", methods=["POST"])
@jwt_required()
def verify_otp():
    try:
        data = request.get_json()
        phone = data.get("phone")
        otp = data.get("otp")
        if not phone or not otp:
            raise BadRequest("Phone number and OTP are required.")
        
        if not otp_service.verify_otp(phone, otp):  
            raise BadRequest("Invalid OTP.")
        
        if auth_service.user_exists(phone):
            response = auth_service.login_user(phone)
            return jsonify(response), 200
        else:
            token = create_access_token(identity=phone, expires_delta=timedelta(minutes=10))
            return jsonify({"redirect": "/register","token": 'Bearer ' + token}), 200
    except  BadRequest as error:
        response = {
        "msg": str(error)
        }
        return jsonify(response), 400
    except Exception as error:
        print(error)
        response = {
        "msg": f"Internal problem {str(error)}"
        }
        return jsonify(response), 500 



# @app.errorhandler(ValueError)
# @app.route('/auth/login', methods=['POST'])
# def login():
#     data = request.get_json()
#     user, token = auth_service.authenticate_user(data['email'], data['password'])
#     if token:
#         if user.profile_picture:
#             # Convert binary data to base64 encoded string
#             profile_picture_base64 = base64.b64encode(user.profile_picture).decode('ascii')
#         response = {
#             "access_token": f"Bearer {token}",
#             "user": {
#                 "email": user.email,
#                 "name": user.name,
#                 "surname": user.surname,
#                 "username": user.username,
#                 "role": user.role.name,
#                 "profile_picture": profile_picture_base64
#             }
#         }
#         return jsonify(response), 200
#     return jsonify({"msg": "Invalid credentials"}), 401
    
   
    # @app.errorhandler(ValueError)
    # @app.route('/auth/set-password', methods=['POST'])
    # @jwt_required()
    # def set_new_password():
    #     try:
    #         data = request.get_json()
    #         user_id = get_jwt_identity()
    #         old_password = data.get('old_password')
    #         new_password = data.get('new_password')

    #         # Ensure required data is provided
    #         if not user_id or not old_password or not new_password:
    #             return jsonify({"msg": "Missing required fields"}), 400

    #         # Call service to handle password update
    #         updated = auth_service.update_password(user_id, old_password, new_password)
    #         if updated:
    #             return jsonify({"msg": "Password updated successfully"}), 200
    #         return jsonify({"msg": "Invalid credentials or password mismatch"}), 401
    #     except ValueError as error:
    #         return jsonify({"msg": str(error)}), 400
    #     except Exception as error:
    #         print(error)
    #         return jsonify({"msg": "Internal problem"}), 500
        
    # # Route to set profile picture
    # @app.route('/user/profile-picture', methods=['POST'])
    # @jwt_required()
    # def set_profile_picture():
    #     picture_url = request.json.get('picture_url')
    #     user_id = get_jwt_identity()
        
    #     user = profile_service.set_profile_picture(user_id, picture_url)
    #     return jsonify({"message": "Profile picture updated", "profile_picture": user.profile_picture})

    # # Route to get profile picture
    # @app.route('/user/profile-picture', methods=['GET'])
    # @jwt_required()
    # def get_profile_picture():
    #     user_id = get_jwt_identity()
    #     print(user_id)
    #     role = get_jwt().get('role')
    #     print(role)
    #     user_picture = profile_service.get_profile_picture(user_id)  # Assuming this returns the image as bytes
    #     if user_picture:
    #     # Convert the image bytes to Base64
    #         base64_image = base64.b64encode(user_picture).decode('utf-8')
    #         return jsonify({"profile_picture": base64_image})
    #     else:
    #         return jsonify({"msg": "No profile picture found"}), 404
