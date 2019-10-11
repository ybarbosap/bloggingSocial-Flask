# Importações
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_moment import Moment
from config import config
from flask_login import LoginManager

# Instâncias
bootstrap = Bootstrap()
db = SQLAlchemy()
moment = Moment()
mail = Mail()
loginManager = LoginManager()

#Configura um endpoint ( rota ) de redirecionamento para página de login quando usuário anônimo tentar acessar uma página protegida.
loginManager.login_view = 'auth/login'

# Inicialização
def createApp(config_name):

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    

    # registro blueprint para usar as rotas e handlers de erro
    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # registro blueprint para rotas de login
    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix = '/auth') # url_prefix é opcional, registra a rota com prefixo especificado
                                                                 # .../auth/login ao invés de .../login

    config[config_name].init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    loginManager.init_app(app)

    return app