from app import db, loginManager
from werkzeug import generate_password_hash, check_password_hash
from flask_login import UserMixin

class Role(db.Model):
    __tablename__ = 'roles'
    __table_args__ = {'extend_existing': True} 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    # relacionamento: o atributo 'users' devolverá uma lista de usuários associados a esta função
    users = db.relationship('User', backref='role')
                            # Este primeiro parâmetro especifica quem esta do outro lado do relacionamento
                            # backref='role' acrescenta um atributo chamado 'role' ao modelo 'User'

    def __repr__(self):
        return '<Role %r>' % self.name

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique = True, index = True)# Index cria um índice para tornar as consultas mais eficientes
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
                                    # especifica que esta coluna deve ser interpretada   
                                    # como tendo valores de de id da tabela 'roles'

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

    def __repr__(self):
        return '<User %r>' % self.username


    @loginManager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    """
    função para carregar dados de usuário, o decorador .user_loader é uasdo para registrar a função
    junto ao Flask-login que a chamará quando precisar obter informações do usuário.
    query.get() retornara um obejto de usuário ou None 
    """