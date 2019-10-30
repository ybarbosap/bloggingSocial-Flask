from flask import (
    render_template, redirect, request, url_for, flash
)
from flask_login import (
    login_user, logout_user, login_required, current_user
)
from app.auth import auth
from ..models import User
from ..import db
from app.auth.forms import (
    LoginForm, RegistrationForm, ChangePasswordForm, ChangeEmail, 
    PasswordResetRequestForm
)
from ..email import send_email

@auth.before_app_request
def before_request():
    # atualizar o campo last_seen sempre que o usuário fizer uma requisição
    if current_user.is_authenticated:
        current_user.ping()

        # Caso usuário não esteje confirmado, redireciona para página 'unconfirmed' após atulizar last_seen
        if not current_user.confirmed \
                and request.endpoint \
                and request.blueprint != 'auth' \
                and request.endpoint != 'static':
            return redirect( url_for('auth.unconfirmed'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()    
     
    if form.validate_on_submit():
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
    return redirect(url_for('.login'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        u = User(email=form.email.data, 
                 username=form.username.data, 
                 password=form.password.data)
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token()
        send_email(u.email, 'Confirm Your Account', 
                    'auth/email/confirm', user=u, token=token)
        flash('You can now login.')
        return redirect(url_for('main.index'))
    
    return render_template('auth/register.html', form=form)


# Confirmar uma conta de usuário
@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    # Se ja está confirmado
    if current_user.confirmed:
        return redirect( url_for( 'main.index' ) )
    if current_user.confirm(token):
        db.session.commit()
        flash(' You have confirmed your account. Thanks! ')
    else:
        flash(' The confimation link is invalid or has expired. ')
    
    return redirect(url_for('main.index'))


# Reenvia o email de confirmação
@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm your account', 
               'auth/email/confirm', 
                user=current_user, 
                token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect( url_for( 'main.index' ))


@auth.route('/chage-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash('Your password has been updated.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password')
    return render_template('auth/change_password.html', form=form)    


@auth.route('/unconfirmed')
def unconfirmed():
    # Se o usuário for anônimo ( não cadastrado ) ou confirmado é enviado para index
    # Caso contrário é redirecionado para página unconfirmed.
    if current_user.is_anonymous or current_user.confirmed:
        return redirect( url_for( 'main.index', 
                        name = current_user.name ))

    return render_template('auth/unconfirmed.html')


@auth.route('/change_email', methods=['POST', 'GET'])
@login_required
def change_email_request():
    form = ChangeEmail()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new = form.new_email.data
            token = current_user.generate_email_change_token(new)
            send_email(new, 'Confirm your email address',
                       'auth/email/change_email',
                       user=current_user, token=token)
            flash('An email with instructions to confirm your new email' 
                  'address has been sent to you.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.')
    return render_template('auth/change_email.html', form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    # Se o usuário não for anônimo, então o mesmo ja logou e 
    # ... será redirecionado para pagina index.
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, 'Reset your password',
                        'auth/email/reset_password',
                        user=user, token=token)
            flash('An email with instructions to reset your password '
                  'has been sent to you')
            redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)    