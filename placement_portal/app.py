
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from models import db, Student, Company, Job, Application



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///placement.db'
db.init_app(app)

with app.app_context():
    db.create_all()