from flask import Blueprint

api = Blueprint('api', __name__)

from . import authentication
from . import comments
from . import users
from . import posts
from . import erros