from modules.Chain import Chain
from flask import request, jsonify
from flask_restplus import Namespace, Resource, fields, reqparse
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from modules.Db.Helper import *
from json import loads, dumps

# Some APIs use API keys for authorization. An API key is a token that a client provides when making API calls. The key can be sent in the query string:
# Swagger convention would be to use 'X-API-KEY' which is the generic API access method
# In we are using jwt extended generating access token with the following header format: Authorization: Bearer 1234567890abcdef

authorizations = {
    'apiKey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}

api = Namespace('api/chainRoute', description='chain route',
                authorizations=authorizations)

parser = reqparse.RequestParser()
parser.add_argument('symbol', type=str, help='type symbol here')


@api.route('/')
class chainRoute(Resource):
    @api.expect(parser, validate=False)
    @api.doc(security="apiKey")
    @jwt_required
    def get(self):

        # get user name to pull out session token
        current_user = get_jwt_identity()
        # getAccountNumber(access_token)
        user = Session.query(User).filter(
            User.username == current_user
        ).one_or_none()

        symbol = parser.parse_args()

        # need to pass in accountId in here not username and parse out json to extract symbol
        chain = Chain.getChainStrikes(
            user.account_number, symbol['symbol']
            )

        print(chain)

        Session.commit()

        return chain, 200
