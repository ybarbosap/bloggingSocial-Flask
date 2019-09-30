from app import db

class Role(db.Model):

    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    # relacionamento: o atributo 'users' devolverá uma lista de usuários associados a esta função
    users = db.relationship('User', backref='role')
                            # Este primeiro parâmetro especifica quem esta do outro lado do relacionamento
                            # backref='role' acrescenta um atributo chamado 'role' ao modelo 'User'

    def __repr__(self):
        return '<Role %r>' % self.name

class User(db.Model):

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
                                                    # Cria um índice para tornar as consultas mais eficientes
    
    # relacionamento 
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
                                    # especifica que esta coluna deve ser interpretada   
                                    # como tendo valores de de id da tabela 'roles'

    def __repr__(self):
        return '<User %r>' % self.username