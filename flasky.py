import os
from app import createApp, db
from app.models import User, Role
from flask_migrate import Migrate

app = createApp(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shel_context():
    return dict(db=db, User=User, Role=Role)