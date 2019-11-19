from flask import render_template 
from flask import url_for 
from flask import current_app
from flask import request 
from flask import make_response
from flask import abort 
from flask import flash 
from flask import redirect 
from flask import session

from app.main import main

from app.main.forms import NameForm
from app.main.forms import EditProfileForm
from app.main.forms import EditProfileAdminForm
from app.main.forms import PostForm
from app.main.forms import DeletePost
from app.main.forms import CommentForm

from app import db

from app.models import User
from app.models import Permission
from app.models import Post
from app.models import Role
from app.models import Comment

from flask_login import current_user
from flask_login import login_required

from ..decorators import admin_required, permission_required


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
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_post
    else:
        query = Post.query
    pagination = query.order_by(Post.timestamp.desc()).paginate(
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


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        newc = Comment(body=form.body.data, 
                       post=post, 
                       author=current_user._get_current_object())
        db.session.add(newc)
        db.session.commit()

        flash('Your comment has been published.')

        """
        page=-1 é usado para requisitar a última página de comentários
        de mode que o comentário de acabou de ser inserido seja visto
        na última página. Os comentários novos ficam na utlimta pagina

        """
        return redirect(url_for('.post', id=post.id, page=-1))

    page = request.args.get('page', 1, type=int)    
    if page ==  -1:
        page = (post.comments.count() - 1 ) // current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
        
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'], error_out=False
        )
    comments = pagination.items
    return render_template('post.html', posts=[post], form=form, comments=comments, pagination=pagination)


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


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    u = User.query.filter_by(username=username).first()
    if u is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    
    if current_user.is_following(u):
        flash('You are already following this user.')
        return redirect(url_for('.user', username=username))
    
    current_user.follow(u)
    db.session.commit()
    flash('You are now following %s', username)
    return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('You are not following this user.')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    flash('You are not following %s anymore.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    u = User.query.filter_by(username=username).first()
    if u is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.app.config['FLASK_FOLLOWERS_PER_PAGE'],
        error_out=False
    )
    follows = [{'user':item.follower, 'timestamp':item.timestamp} for item in pagination.items]
    return render_template('followes.html', user=user, title='Followers of', endpoint='.followers',
                           pagination=pagination, follows=follows)


@main.route('/followed-by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp} for item in pagination.items]
    return render_template('followers.html', user=user, title="Followed by",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)


@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=90*24*60*60)
    return resp


@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('moderate.html', comments=comments,
                           pagination=pagination, page=page)


@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE)
def moderate_enable(id):
    coment = Comment.query.get_or_404(id)
    coment.disabled = False
    db.session.add(coment)
    db.session.commit()
    return redirect(url_for('.moderate',
                    page=request.args.get('page', 1, type=int)))


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE)
def moderate_disable(id):
    coment = Comment.query.get_or_404(id)
    coment.disabled = True
    db.session.add(coment)
    db.session.commit()
    return redirect(url_for('.moderate',
                    page=request.args.get('page', 1, type=int)))