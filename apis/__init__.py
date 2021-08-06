# from flask import Flask, Blueprint
# from flask_restplus import Api, apidoc
from flask_restx import Api

# from complex import app
from .namespace0 import api as login
from .namespace1 import api as protected
from .namespace2 import api as chainRoute
from .namespace3 import api as addorder
from .namespace4 import api as deleteorder
from .namespace5 import api as confirm
from .namespace6 import api as stageorder
from .namespace7 import api as price
from .namespace8 import api as placed
from .namespace9 import api as deleteplaced

# add the following inside Api to remove swagger page from ui: doc = False
api = Api(
    title='Qtrack API Framework',
    version='1.0',
    description='hedge platform'
)

api.add_namespace(login)
api.add_namespace(protected)
api.add_namespace(chainRoute)
api.add_namespace(addorder)
api.add_namespace(deleteorder)
api.add_namespace(confirm)
api.add_namespace(stageorder)
api.add_namespace(price)
api.add_namespace(placed)
api.add_namespace(deleteplaced)

