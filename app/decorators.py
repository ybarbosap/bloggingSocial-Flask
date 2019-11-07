from functools import wraps
from flask import abort
from flask_login import current_user
from .models import Permission

# ---- Rever futuramente para entender melhor esse código ---- #
def permission_required(permission):
    
    def decorator(f):   
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # o código de status HTTP 403 retorna "Forbidden ( Proibido )"
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    return permission_required(Permission.ADMIN)(f)
    