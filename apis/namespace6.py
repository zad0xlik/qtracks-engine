from flask import request, jsonify
from flask_restplus import Namespace, Resource, fields
from json import loads, dumps
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from modules.Order import OrderHandler

authorizations = {
    'apiKey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}

api = Namespace('api/stageorder', description='stage an order')

legParams = api.model('leg', {
    'orderLegType': fields.String(required=True, description='order Leg Type'),
    'assetType': fields.String(required=True, description='asset Type'),
    'symbol': fields.String(required=True, description='symbol'),
    'instruction': fields.String(required=True, description='instruction'),
    'quantity': fields.String(required=True, description='quantity')
})


params = api.model('stageorder', {
    'accountId': fields.String(required=True, description='account id'),
    'session': fields.String(required=True, description='session'),
    'duration': fields.String(required=True, description='duration'),
    'legs': fields.List(fields.Nested(legParams)),
    'orderStrategyType': fields.String(required=True, description='order Strategy Type'),
    'price': fields.String(required=True, description='price')
})

@api.route('/')
class stageorder(Resource):
    @api.doc(security="apiKey")
    @api.expect(params, validate=True)
    @jwt_required
    def post(self):

        if not request.is_json:
            return jsonify({"msg": "Missing JSON in request"}), 400

        parameters = request.get_json()

        accountId = parameters['accountId']
        session = parameters['session']
        duration = parameters['duration']
        legs = parameters['legs']
        orderStrategyType = parameters['orderStrategyType']
        price = parameters['price']

        if not accountId:
            return jsonify({"msg": "Missing accountId parameter"}), 400
        if not session:
            return jsonify({"msg": "Missing session parameter"}), 400
        if not duration:
            return jsonify({"msg": "Missing duration parameter"}), 400
        if not legs:
            return jsonify({"msg": "Missing legs parameter"}), 400
        if not orderStrategyType:
            return jsonify({"msg": "Missing orderStrategyType parameter"}), 400
        if not price:
            return jsonify({"msg": "Missing price parameter"}), 400

        order = request.get_json()
        OrderHandler.updateOrderStatus(order)
        return dumps({'operation':'success'}), 200