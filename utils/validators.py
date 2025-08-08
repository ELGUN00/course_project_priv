from werkzeug.exceptions import BadRequest

def validate_registration(data):
    if not data.get("role") or data["role"].lower() not in ["student", "academy", "tutor"]:
        raise BadRequest("Role must be one of: student, academy, tutor.")