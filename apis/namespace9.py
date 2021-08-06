from flask import request, jsonify
from flask_restplus import Namespace, Resource, fields
from json import loads, dumps
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from modules.Db.Helper import *
from modules.Order import Order

authorizations = {
    'apiKey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}


api = Namespace('api/deleteplaced', description='delete placed order',
                authorizations=authorizations)

params = api.model('deleteplaced', {
    'orderId': fields.List(fields.String(description='order to delete'))
})


@api.route('/')
class deleteplaced(Resource):
    @api.doc(security="apiKey")
    @jwt_required
    def delete(self):
        if not request.is_json:
            return jsonify({"msg": "Missing JSON in request"}), 400

        parameters = request.get_json()

        orderId = parameters['orderId']

        if not orderId:
            return jsonify({"msg": "Missing symbols parameter"}), 400
        # get user name to pull out session token
        current_user = get_jwt_identity()
        user = Session.query(User).filter(
            User.username == current_user
            ).one_or_none()
        Session.commit()
        orders = Order.deleteOrder(user.account_number, orderId)
        if(orders):
            return dumps(orders), 200
        return dumps({'response': 'no order found'}), 200