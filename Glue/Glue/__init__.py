"""
The flask application package.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os.path

app = Flask(__name__)

app.config.from_json(os.path.join(app.root_path, 'config.json'))

db = SQLAlchemy(app)

import Glue.models

db.create_all()

import Glue.views
