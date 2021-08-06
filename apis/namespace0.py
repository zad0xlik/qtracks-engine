from flask import request, jsonify
from flask_restplus import Namespace, Resource, fields
from json import loads, dumps
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from json import loads
from modules.Auth import Auth
from modules.Db.Helper import *
from modules.Db import Redis


api = Namespace('api/login', description='this is the login api')

params = api.model('login', {
    'username': fields.String(required=True, description='username'),
    'password': fields.String(required=True, description='password'),
    'client_id': fields.String(required=True, description='client_id (e.g. OSP8IKN8RIL91USENMD0SMOLEXRSQ6BP)')
})

# 'token_key': fields.String(required=True, description='this is init auth access code referred to access_code')

# Provide a method to create access tokens. The create_access_token()
# function is used to actually generate the token, and you can return
# it to the caller however you choose.
@api.route('/')
class login(Resource):
    @api.expect(params, validate=True)
    def post(self):
        if not request.is_json:
            return jsonify({"msg": "Missing JSON in request"}), 400

        parameters = request.get_json()

        username = parameters["username"]
        password = parameters["password"]
        client_id = parameters["client_id"]

        if not username:
            return dumps(
                {
                    "msg": "Missing username parameter"
                }
            ), 400

        if not password:
            return dumps(
                {
                    "msg": "Missing password parameter"
                }
            ), 400
        
        storedUser = Session.query(User).filter(User.username == username).first()
        if not storedUser:
            return dumps(
                {
                    "msg": "Bad username or password"
                }
            ), 401
        if(not storedUser.check_password(password)):
            return dumps(
                {
                    "msg": "Bad username or password"
                }
            ), 401

        access_code = Auth.initAccessCode(client_id, username, password)
        access_token = Auth.initAccessToken(client_id, access_code)
        access_token_internal = create_access_token(identity=username)

        Redis.r.set(f'{username}_refresh_token', access_token['refresh_token'])
        Redis.r.set(f'{username}_access_token', access_token['access_token'])
        Redis.r.expire(f'{username}_access_token', 1500)

        response = dumps(
            {
                "access_token": access_token_internal,
                "account_number": storedUser.account_number,
                "acccess_token": access_code,
                "acccess_token": access_token
            }
        )
        Session.commit()

        return response, 200
