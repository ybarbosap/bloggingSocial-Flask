from flask import render_template, url_for, session, redirect
from app.main import main
from app.main.forms import NameForm
from app import db
from app.models import User

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