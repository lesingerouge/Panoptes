# system imports
import datetime, string, random
# framework imports
from flask import current_app
# app imports
from .. import mongo
from ..core import BaseDocument
from ..core.viewhelpers import DataTableHelper
from forms import ServiceForm


class Services(BaseDocument,DataTableHelper):
    """
    Model for all the services that need to be monitored by the app
    """
    fromdict = {
                "server" : {"dbfield":"ip", "required":True, "verbose":"IP server"},
                "port" : {"dbfield":"po", "required":True, "verbose":"Port server"},
                "service_type" : {"dbfield":"st", "required": True, "verbose":"Tip serviciu"},
                "last_check" : {"dbfield":"ls", "verbose":"Ultima verificare"},
                "active" : {"dbfield":"at", "verbose":"Activ", "default":True, "validate":bool},
                "authentication" : {"dbfield":"au", "verbose":"Autentificare"}
                }

    db = mongo.db
    collection = "services"
    show_fields = ["server","port","service_type","last_check","active"]
    button_field = True
    
    def __init__(self, **kwargs):
        BaseDocument.__init__(self,**kwargs)


    @classmethod
    def get_active(cls,group_by_type=True):

        raw_results = [x for x in cls.connection().find({"at":True})]
        if group_by_type:
            groups = set([x['st'] for x in raw_results])
            results = {x:[] for x in groups}
            for item in raw_results:
                results[item["st"]].append(cls(values=item))

        else:
            results = {"ungrouped":[cls(values=item) for item in raw_results]}

        return results


    def get_form(self):

        return ServiceForm()