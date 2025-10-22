from flask import Flask
from flask_cors import CORS
from config import Config
from controllers.auth_controller import auth_bp
from controllers.course_controller import course_bp
from controllers.comment_controller import comment_bp
from controllers.user_controller import user_bp
from controllers.pageview_controller import page_view_bp
from controllers.favorites_contoller import favorites_bp
from controllers.search_controller import search_bp
from extensions import db, jwt, es
from flask_talisman import Talisman
from flask_migrate import Migrate
# Initialize Flask app and configuration
app = Flask(__name__)
app.debug = True
talisman = Talisman(app)
CORS(app)

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(course_bp, url_prefix='/course')
app.register_blueprint(comment_bp, url_prefix='/comment')
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(page_view_bp, url_prefix='/pageview')
app.register_blueprint(favorites_bp, url_prefix='/favorites')
app.register_blueprint(search_bp, url_prefix='/search')

# Trust the proxy (because Apache is forwarding traffic to Flask over HTTP)
app.config['PREFERRED_URL_SCHEME'] = 'https'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
# Enable this to avoid potential problems with Flask's `url_for` function
app.config['SESSION_COOKIE_SECURE'] = True 

app.config.from_object(Config)

db.init_app(app)
jwt.init_app(app)

# NEW: Initialize Migrate
migrate = Migrate(app, db)

# auth_service = AuthenticationService(db.session)
# profile_service = ProfileService(db.session)

from _logger import log

if __name__ == '__main__':
    # Initialize database and create tables
    # Ensure app context is available
    

    es.options(ignore_status=[400]).indices.create(index="users")
    es.options(ignore_status=[400]).indices.create(index="courses")
    log('Hello world!')
    # with app.app_context():
    #     db.create_all()  # Create all tables
    app.run(
        host="0.0.0.0",           # Listen on all interfaces
        port=5002,                # HTTPS default port
    )
    # ssl_context=("./apache2.crt", "./apache2.key")
    #app.run(host="0.0.0.0", port=5000,debug=True)
