# system imports
import datetime, string, random
# framework imports
from werkzeug import generate_password_hash, check_password_hash
from flask import current_app
from flask.ext.login import UserMixin, current_user
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
# app imports
from .. import mongo, login_manager
from ..core import BaseDocument
from ..core.viewhelpers import DataTableHelper
from forms import UserForm
from ..config import Config


class Users(UserMixin,BaseDocument,DataTableHelper):
    """
    Model for all the users in the app
    """
    fromdict = {
                "username" : {"dbfield":"un", "required":True, "verbose":"Nume utilizator"},
                "email" : {"dbfield":"em", "required":True, "unique":True, "verbose":"Email"},
                "pswd" : {"dbfield":"pw", "required": True},
                "permissions" : {"dbfield":"pm", "required":True, "verbose":"Permisiuni"},
                "last_seen" : {"dbfield":"ls", "verbose":"Ultima vizita", "default":datetime.datetime.now},
                "active" : {"dbfield":"at", "verbose":"Activ", "default":True, "validate":bool}
                }

    db = mongo.db
    collection = "users"
    show_fields = ["username","email","active","last_seen"]
    button_field = True
    
    def __init__(self, **kwargs):
       BaseDocument.__init__(self,**kwargs)


    @property
    def password(self):
        raise AttributeError('Parola nu poate fi accesata direct')


    @password.setter
    def password(self,passwd):
        self.pswd.value = generate_password_hash(passwd)


    def random_password(self):
        """
        Used to generate a random password for new users
        """
        temp_pass = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        self.password = temp_pass
        return temp_pass


    def verify_password(self,passwd):
        return check_password_hash(self.pswd.value,passwd)


    def generate_reset_token(self, expiration=7200):
        """
        Used to generate a password reset token for a user account
        """
        s = Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'reset': unicode(self.id)})


    def resetpass(self,token):
        """
        Used to check for the reset password token for a user account
        """
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        if data.get('reset') != unicode(self._id.value):
            return None
        return self._id.value


    def ping(self):
        self.last_seen.value = datetime.datetime.now()


    def is_active(self):
        return self.active.value


    def get_id(self):
        return self._id.value


    def messages(self):
        pass


    def is_admin(self):
        return self.permissions.value == config.PERMISSIONS['admin']


    def is_manager(self):
        return self.permissions.value == config.PERMISSIONS['manager']


    @classmethod
    def get_form(cls):

        return UserForm()


@login_manager.user_loader
def load_user(user_id):
    try:
        user = Users.get({"_id":user_id})
        return user
    except:
        return None