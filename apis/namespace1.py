from flask import request, jsonify
from flask_restplus import Namespace, Resource, fields
from flask_jwt_extended import (create_access_token
                                , create_refresh_token
                                , jwt_required
                                , jwt_refresh_token_required
                                , get_jwt_identity
                                , get_raw_jwt)
from json import loads, dumps

# Some APIs use API keys for authorization. An API key is a token that a client provides when making API calls. The key can be sent in the query string:
# Swagger convention would be to use 'X-API-KEY' which is the generic API access method
# In we are using jwt extended generating access token with the following header format: Authorization: Bearer 1234567890abcdef

authorizations = {
    'apiKey' : {
        'type' : 'apiKey',
        'in'   : 'header',
        'name' : 'Authorization'
    }
}

api = Namespace('api/protected'
                , description='Protect a view with jwt_required, which requires a valid access token in the request to access. To use this api from swagger, copy access token from login, click on the lock icon and type "Bearer [access_token]".'
                , authorizations=authorizations)

# Protect a view with jwt_required, which requires a valid access token
# in the request to access.
@api.route('/')
class protected(Resource):
    @api.doc(security="apiKey")
    @jwt_required
    def get(self):

        # Access the identity of the current user with get_jwt_identity
        current_user = get_jwt_identity()

        response = dumps(
            {
                "user": current_user
            }
        )
        return response, 200