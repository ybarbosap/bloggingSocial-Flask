from flask import (
    render_template, url_for, session, redirect, flash, abort, request, current_app,
    abort
)
from app.main import main
from app.main.forms import NameForm, EditProfileForm, EditProfileAdminForm, PostForm, DeletePost
from app import db
from app.models import User, Permission, Post, Role
from flask_login import login_required, current_user
from ..decorators import admin_required


@main.route('/', methods=['GET', 'POST'])
def index(): 
    form = PostForm()
    if current_user.is_authenticated:
        if current_user.can(Permission.WRITE) and form.validate_on_submit():
            post = Post(body=form.body.data,
                        author=current_user._get_current_object())
            db.session.add(post)
            db.session.commit()
            return redirect(url_for('.index'))

    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], 
        error_out=False
    )
    posts = pagination.items
    return render_template('index.html', form=form, posts=posts,
                           pagination=pagination)


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter_by(author=current_user._get_current_object()
                                      ).paginate(page, 
                                      per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], 
                                      error_out=False
    )
    posts = pagination.items
    return render_template('user.html', user=user, posts=posts,
                           pagination=pagination)


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


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)

    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = form.role.data
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        
        db.session.add(user)
        db.session.commit()

        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))

    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html', posts=[post])


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
        not current_user.can(Permission.ADMIN):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        flash('The post has been updated.')
        return redirect(url_for('.post', id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form)


@main.route('/delet/<int:id>', methods=['GET', 'POST'])
@login_required
def delet_post(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
        not current_user.can(Permission.ADMIN):
        abort(403)
    form = DeletePost()
    if form.validate_on_submit():
        db.session.delete(post)
        db.session.commit()
        flash('Your post has ben deleted.')
        return redirect(url_for('.user', username=current_user.username))
    return render_template('del_post.html', form=form, post=post)