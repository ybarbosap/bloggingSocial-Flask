import os
from app import createApp, db
from app.models import User, Role, Post, Permission
from flask_migrate import Migrate

app = createApp(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)


# Os processadores de contexto deixam as variáveis disponíveis a todos os templates durante a renderização
@app.shell_context_processor
def make_shel_context():
    return dict(db=db, User=User, Role=Role, Permission=Permission,
                Post=Post)


@app.cli.command()
def test():
    """Run the unit test"""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)