from flask import (
    render_template, redirect, request, url_for, flash
)
from flask_login import (
    login_user, logout_user, login_required
)
from app.auth import auth
from ..models import User
from app.auth.forms import LoginForm

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    # requisição do tipo POST 
    if form.validate_on_submit():
        # carrega um objeto funcionário do banco usando um e-mail fornecido pelo formulário
        user = User.query.filter_by(email=form.email.data).first()

        # Se for encontrado um usuário o método verify_password valida a senha 
        if user is not None and user.verify_password(form.password.data):
            # login_user registra um usuário como logado [ login_user(<usuario para login>, <booleano para lembrar do usuário ao fechar o navegado>)]
            login_user(user, form.rememberMe.data)
            # o argumento next salva o URL anterior ao usuário tentar acessar uma página protegida
            next = request.args.get('next')

            if next is None or not next.startwith('/'):
                next = url_for('main.index')
            
            return redirect(next)
        flash('Invalid username or password!')
    
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required 
def logout():
    logout_user()
    flash('You have been logged out.')

    return redirect(url_for('main.index'))