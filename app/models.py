import hashlib
from app import db, loginManager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin, login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request
from datetime import datetime


class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16


class Role(db.Model):    
    __tablename__ = 'roles'
    __table_args__ = {'extend_existing': True} 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    # relacionamento: o atributo 'users' devolverá uma lista de usuários associados a esta função
    users = db.relationship('User', backref='role', lazy='dynamic')
                            # Este primeiro parâmetro especifica quem esta do outro lado do relacionamento
                            # backref='role' acrescenta um atributo chamado 'role' ao modelo 'User'


    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0


    def __repr__(self):
        return '<Role %r>' % self.name


    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm


    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -+ perm


    def reset_permission(self):
        self.permissions = 0


    def has_permission(self, perm):
        return self.permissions & perm == perm



    """
    => staticmethod ( método estático ) : representa um método que não exige que um objeto seje criado ( instânciado )
    podendo ser chamado diretamente na classe <EX: Role.insert_roles() > ...Métodos estáticos não aceitam um argumento
    self como métodos de instância ( classmethod )

    => line 80 : O construtor de User inicialmente chama os contrutores das classes-bases; se, objeto não tiver uma fu
    nção de usuário definida, a função de Administrador ou a função default será atribuida, dependendo do endereço de 
    email.

    """
    @staticmethod
    def insert_roles():
        roles = {
            'User' : [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            'Moderator' : [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE, Permission.MODERATE],
            'Administrator' : [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE, Permission.MODERATE, Permission.ADMIN]
        }
        default_role = 'User'

        for r in roles:
            role = Role.query.filter_by(name=r).first()
            
            if role is None:
                role = Role(name=r)
            
            role.reset_permission()
            
            for perm in roles[r]:
                role.add_permission(perm)
            
            role.default = (role.name == default_role)
            db.session.add(role)

        db.session.commit()


class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True} 
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique = True, index = True)# Index cria um índice para tornar as consultas mais eficientes
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    #seguindo
    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    #seguidores
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')


    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASK_ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = self.gravatar_hash()


 # tratamento de erro para consulta a password
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
  

    @password.setter
    def password(self, password):
        # cria uma senha criptografada
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        # faz a comparação entre a senha do db e a senha fornecida para login
        return check_password_hash(self.password_hash, password)

    # Confirmação de email
    def generate_confirmation_token(self, expiration = 3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({ 'confirm': self.id }).decode('utf-8')     
    

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps(
            {'change_email':self.id, 'new_email':new_email}
        ).decode('utf-8')


    def generate_reset_token(self, expiration=3600):
        # Gera um JSONs (JSON WEB SIGNATURES) com time de encerrametno
        # ... o dumps() gera uma assinatura com o id passado
        # ... e retorna os dados e a assinatura como uma string
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset':self.id}).decode('utf-8')

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = self.gravatar_hash()
        db.session.add(self)
        return True


    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])        
        
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        
        if data.get('confirm') != self.id:
            return False
        
        self.confirmed = True
        db.session.add(self)
        return True


    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)


    def is_administrator(self):
        return self.can(Permission.ADMIN)


    # last_seen é inicializado com o horário atual, mas deve ser atualizado sempre que o usuário acessar o site
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)


    def __repr__(self):
        return '<User %r>' % self.username


    def gravatar_hash(self):
        return hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()
    
    
    def gravatar(self, size=100, default='identicon', rating='g'):
        url = 'https://secure.gravatar.com/avatar'
        hash = self.avatar_hash or self.gravatar_hash()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)


    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)
    

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=iser.id).first()
        if f:
            db.session.delete(f)
    

    #está seguindo
    def is_following(self, user):
        if user.id is None:
            return False
        return self.followed.filter_by(
            followed_id=user.id
        ).first() is not None
    

    def is_followed_by(self, user):
        if user.id is None:
            return False
        return self.followers.filter_by(
            follower_id=user.id
        ).first() is not None
    
    # Faz uma query na tabela Post
    # Pede um join passando a tabela Follow ( cria uam tablea temporaria ( tabela pivô ))
    # Usa o id seguido == id do autor do Post ( Define os parâmetros da tabela de junção, onde todo folloed_id faz math com post.author_id )
    # Filtra para mostrar apenas os que tenhas como seguidor o id do usuário atual do sistema 
    @property
    def followed_post(self):
        return Post.query.join(Follow, Follow.followed_id == Post.author_id).filter(Follow.follower_id == self.id)
    # limito o retorno apanas para usuários que estão na tabela seguido e tenham feito um post, depois filtro apenas os usuário que tem o meu id como seguidor


    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()


@loginManager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Post(db.Model):
    __tablename__='posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))


"""

função para carregar dados de usuário, o decorador .user_loader é uasdo para registrar a função
junto ao Flask-login que a chamará quando precisar obter informações do usuário.
query.get() retornara um obejto de usuário ou None 

"""

"""
    -- Confirmação do usuário
O construtor de TimedJSONWebSignatureSerializer aceita uma chave que em Flask pode ser a SECRET_KEY.
O método dumps() gera uma assinatura cripitografada, o argumento expiration define um tempo expresso 
em segundos para o token expirar. 
Para decodificar o token o TimedJSONWebSignatureSerializer disponibiliza o loads() que confere a 
assinatura e o prazo de validade, se ambos forem válidos, devolve os dados originais.

"""