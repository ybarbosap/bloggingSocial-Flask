from flask import (
    render_template, url_for, session, redirect, flash
)
from app.main import main
from app.main.forms import (
    NameForm, EditProfileForm
)
from app import db
from app.models import User
from flask_login import (
    login_required, current_user
)

@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()

        if user is None:
            user = User(username = form.name.data)
            db.session.add(user)
            db.session.commit()

            session['known'] = False
        
        else:
            session['known'] = True
        
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('main.index'))

    return render_template('index.html', form=form, name=session.get('name'), 
                            known=session.get('known', False))


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():

    form = EditProfileForm()

    # atualizando os registros com as novas informações 
    if form.validate_on_submit():
        
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data

        db.session.add(current_user._get_current_object())
        db.session.commit()

        flash('Your profile has been updated')

        return redirect(url_for('main.user', username = current_user.username))
    
    # Se form.validate_on_submit() for False, os campos serão inicializados com os valores de current_user
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me

    return render_template('edit_profile.html', form=form)