from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from elasticsearch import Elasticsearch

db = SQLAlchemy()
jwt = JWTManager()
es = Elasticsearch("http://elasticsearch:9200")