from flask import Blueprint

auth = Blueprint('auth', __name__)

from app.auth import views

"""
Blueprint para rotas de autenticação
"""