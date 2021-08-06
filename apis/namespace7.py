from flask import request, jsonify
from flask_restplus import Namespace, Resource, fields
from json import loads, dumps
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from modules.Db.Helper import *
from modules.Pricing import PriceApi
from modules.Auth import Auth

authorizations = {
    'apiKey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}


api = Namespace('api/price', description='Price a list of symbols',
                authorizations=authorizations)

params = api.model('price', {
    'symbols': fields.List(fields.String(description='Symbols to calculate')),
})


@api.route('/')
class price(Resource):
    @api.expect(params, validate=True)
    @api.doc(security="apiKey")
    @jwt_required
    def post(self):

        if not request.is_json:
            return jsonify({"msg": "Missing JSON in request"}), 400

        parameters = request.get_json()

        symbols = parameters['symbols']

        if not symbols:
            return jsonify({"msg": "Missing symbols parameter"}), 400

        # get user name to pull out session token
        current_user = get_jwt_identity()
        # getAccountNumber(access_token)
        user = Session.query(User).filter(
            User.username == current_user
            ).one_or_none()
        Session.commit()
        toPrice = request.get_json()
        prices = PriceApi.price(user.account_number, toPrice['symbols'])
        return dumps(prices), 200