# system imports
import os, json


basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """
    Class used to hold configurations that are used in both website and admin applications
    """

    MONGO_HOST = "localhost"
    MONGO_DBNAME = "panoptes"

    THREADS_PER_PAGE = 8

    mailcfg = json.load(open('mailcfg.json'))
    MAIL_SERVER = mailcfg['MAIL_SERVER']
    MAIL_PORT = mailcfg['MAIL_PORT']
    MAIL_USE_TLS = mailcfg['MAIL_USE_TLS']
    MAIL_USERNAME = mailcfg['MAIL_USERNAME']
    MAIL_PASSWORD = mailcfg['MAIL_PASSWORD']
    MAIL_ADDRESS = mailcfg['MAIL_ADDRESS']

    PERMISSIONS = {'admin':3, 'manager':2, 'user':1}

    SERVICE_TYPES = ["mongo","redis"]
    SERVICES = [('/services/db/'+x,'services',x.title()) for x in SERVICE_TYPES]
    SERVICES += [('/services/setari/lista','services','Settings')]

    MENU = [('services.home','hardware','Hardware',''),('services.home','services','Software services',SERVICES),('services.home','hardware','App','')]

    
    @staticmethod
    def init_app(app):
        pass


class DevConfig(Config):
    """
    Class used to hold admin-specific configurations
    """

    SECRET_KEY = 'hardtoguesstring'

    DEBUG = True
    ADMINS = json.load(open('admins.json'))

    CSRF_ENABLED = False
    CSRF_SESSION_KEY = "somethingimpossibletoguess"


class AdminConfig(Config):
    """
    Class used to hold admin-specific configurations
    """

    SECRET_KEY = 'hardtoguesstring'

    DEBUG = False
    ADMINS = json.load(open('admins.json'))

    CSRF_ENABLED = True
    CSRF_SESSION_KEY = "somethingimpossibletoguess"

        

config = {
    'dev': DevConfig,
    'admin':AdminConfig
}
