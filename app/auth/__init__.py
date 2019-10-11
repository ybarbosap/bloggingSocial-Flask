from flask import Blueprint

auth = Blueprint('auth', __name__)

from app.auth import views, forms

"""
Blueprint para rotas de autenticação
"""