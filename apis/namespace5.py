import time
from json import loads, dumps
from flask import request, jsonify
from flask_restplus import Namespace, Resource, fields
from json import loads, dumps
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from modules.Order import OrderHandler
from modules.Auth import Auth
from modules.Db.Helper import *
from modules.Db import Redis

api = Namespace('api/confirm', description='this is the register api')

params = api.model('confirm', {
    'username': fields.String(required=True, description='username'),
    'password': fields.String(required=True, description='password'),
    'token_key': fields.String(required=True, description='token_key')
})

@api.route('/')
class confirm(Resource):
    @api.expect(params, validate=True)
    def post(self):

        if not request.is_json:
            return jsonify({"msg": "Missing JSON in request"}), 400

        parameters = request.get_json()
        username = parameters["username"]
        password = parameters["password"]
        token_key = parameters["token_key"]

        if not username:
            return jsonify({"msg": "Missing username parameter"}), 400
        if not password:
            return jsonify({"msg": "Missing password parameter"}), 400
        if not token_key:
            return jsonify({"msg": "Missing token_key parameter"}), 400

        """
        Check if the username already exists
        """
        exists = Session.query(User).filter(
            User.username == username
        ).first()
        if(exists is not None):
            return jsonify(operation='failed'), 400
        """
        Get the user's access token with the approved access key
        """
        access_token = Auth.getAuthNewUser(token_key)
        if(access_token):
            """
            Get the user's account number
            """
            account_number = Auth.getAccountNumber(
                access_token['access_token']
            )
            if(account_number):
                """
                Save the new user in postgres
                """
                user = User(username=username
                            , account_number=account_number
                            )
                user.set_password(password)
                """
                Save tokens in Redis
                """
                Redis.r.set(f'{username}_refresh_token', access_token['refresh_token'])
                Redis.r.set(f'{username}_access_token', access_token['access_token'])
                Redis.r.expire(f'{username}_access_token', 1500)
                
                Session.add(user)
                Session.commit()
                return dumps({'operation': 'success'}), 200
        Session.commit()
        return dumps({'operation': 'failed'}), 400
