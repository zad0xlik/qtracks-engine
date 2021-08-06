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


api = Namespace('api/placed', description='orders placed on TDAmeritrade',
                authorizations=authorizations)

params = api.model('placed', {
    
})


@api.route('/')
class placed(Resource):
    @api.doc(security="apiKey")
    @jwt_required
    def get(self):
        # get user name to pull out session token
        current_user = get_jwt_identity()
        user = Session.query(User).filter(
            User.username == current_user
            ).one_or_none()
        Session.commit()
        orders = Order.getOrdersByPath(user.account_number)
        if(orders):
            return dumps(orders), 200
        return dumps({'response': 'no orders'}), 200