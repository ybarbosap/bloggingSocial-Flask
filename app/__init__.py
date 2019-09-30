# Importações
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_moment import Moment
from config import config

# Instâncias
bootstrap = Bootstrap()
db = SQLAlchemy()
moment = Moment()
mail = Mail()

# Inicialização
def createApp(config_name):

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)

    # registro para usar as rotas e handlers de erro
    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app