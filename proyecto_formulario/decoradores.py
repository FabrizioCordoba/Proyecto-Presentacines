from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def rol_requerido(rol):
    """
    Decorador para verificar el rol del usuario antes de ejecutar una función.
    """
    def decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != rol:
                flash("Acceso denegado.", "danger")
                return redirect(url_for("auth.login"))
            return func(*args, **kwargs)
        return wrapped
    return decorator
