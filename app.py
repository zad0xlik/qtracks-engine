from json import dumps
from apis import api
import json
import os
import time
from flask import Flask, jsonify, request

from flask_jwt_extended import JWTManager
from pathlib import Path
from flask_cors import CORS
from modules.Chain import Chain
from modules.Order import OrderHandler
from modules.Auth import Auth
from modules.Db.Helper import *
from sqlalchemy import and_



app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

# Setup SQLAlchemy helper
@app.teardown_appcontext
def cleanup(exception=None):
    Session.remove()


# Setup the Flask-JWT-Extended extension
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 604800
jwt = JWTManager(app)

api.init_app(app)

if __name__ == '__main__':
    context = ('/etc/letsencrypt/live/bidasktrader.com/cert.pem',
               '/etc/letsencrypt/live/bidasktrader.com/privkey.pem')
    # app.run(host='0.0.0.0', ssl_context=context)
    app.run(host='0.0.0.0')
