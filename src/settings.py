
# Imports

import os
from flask_pymongo import PyMongo
from flask import Flask

# Settings and configurations

PORT = 5000

app = Flask(__name__)

app.config['MONGO_URI'] = f"mongodb+srv://maxipaulino:{os.environ.get('MONGO_PASSWORD')}@cluster0.ibeupug.mongodb.net/Testify?retryWrites=true&w=majority"
myclient = PyMongo(app)
mycol = myclient.db.Questions

# Optimized