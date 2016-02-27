# system imports
from functools import wraps
# framework imports
from flask import flash, redirect, request
from flask.ext.login import current_user,login_required


def manager_required(f):
    @login_required
    @wraps(f)
    def decorated_function(*args,**kwargs):
        if not (current_user.is_manager() or current_user.is_admin()):
            flash('Nu puteti face aceasta operatie!', category='alert-danger')
            return redirect(request.referrer)
      
        return f(*args,**kwargs)

    return decorated_function