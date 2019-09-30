from flask import render_template
from app.main import main


@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
                                        # status code da requisição


@main.app_errorhandler(500)
def internal_server_erro(e):
    return render_template('500.html'), 500
                                        # status code da requisição
