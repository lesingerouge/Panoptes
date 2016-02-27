# system imports
import os

# framework imports
from flask import Flask, render_template, redirect, url_for
from flask.ext.pymongo import PyMongo
from flask.ext.login import LoginManager
from flask.ext.mail import Mail

# app imports
from config import config
from core.sessionhelpers import MongoSessionInterface


#setup for various utilities
mongo = PyMongo()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'users.login'
login_manager.login_message = 'Va rugam sa va logati pentru a accesa aceasta pagina!'
login_manager.login_message_category = 'alert-info'
mail = Mail()


def create_admins(app,admin):
    '''
    used in the create_app function to check if the admins need to be created and create them if needed

    INPUT: dict
    OUPUT: none

    '''
    from users.models import Users
    try:
        user = Users.get({"email": admin['email']})
    except Exception as e:
        user = Users(values={"email": admin['email'],"username": admin['username'],"permissions": 3, "active":True})
        user.password = admin['password']
        user.save()




def create_app(config_name="dev"):
    '''
    used to create the admin app instance

    INPUT: none
    OUTPUT: app instance

    '''
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(config[config_name])
        
    mongo.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    app.session_interface = MongoSessionInterface(db=config[config_name].MONGO_DBNAME)
    
    #ugly temporary hack; server caches classes in app context
    with app.app_context():
        import users.models
        import services.models

    create_admins(app,config[config_name].ADMINS)


    #errorhandlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    #general routes
    @app.route('/')
    def homepage():
        return redirect('/home')

    #filters
    def is_hidden_field(field):
        from wtforms import HiddenField
        return isinstance(field, HiddenField)

    app.jinja_env.globals['bootstrap_is_hidden_field'] = is_hidden_field

    from .users.views import mod as usersBlueprint
    app.register_blueprint(usersBlueprint,url_prefix='')
    from .services.views import mod as dbstatusBlueprint
    app.register_blueprint(dbstatusBlueprint,url_prefix='/services')
    
    return app
