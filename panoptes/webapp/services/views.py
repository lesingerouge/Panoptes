# system imports
import datetime
# framework imports
from flask import Blueprint, request, render_template, flash, redirect, url_for, session, current_app, jsonify
from flask.ext.login import login_required, current_user
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
# app imports
from ..users import manager_required
from models import Services
from forms import ServiceForm
from plugins import REGISTERED_SERVICES


mod = Blueprint('services',__name__)


@mod.before_request
def before_request():
    session['menu'] = current_app.config['MENU']
    session['activemenu'] = 'services'


@mod.route('/setari/lista')
@manager_required
@login_required
def list_services():
    """
    Generates a list of all the registered services that can be checked
    """
    return render_template('services/settings/list_services.html', pagetitle='Lista servicii', results=url_for('services.get_results'), table_head=Services.table_head(), columns=Services.datatables_columns())


@mod.route('/setari/adauga', methods=['GET','POST'])
@manager_required
@login_required
def add_service():
    """
    Used to register a new service
    """

    form = ServiceForm()

    if form.validate_on_submit():
        try:
            srv = Services()
            srv.populate_from_form(form)
            srv.authentication.value = {"db":request.form.get('authdb'),"user":request.form.get('authuser'),"pswd":request.form.get("authpass")}
            srv.save()
            flash('Datele au fost adaugate!', category='alert-success')
            return redirect(url_for('services.list_services'))
        except Exception as err:
            flash('Datele nu pot fi adaugate!', category='alert-danger')

    return render_template('services/settings/add.html', pagetitle='Adauga serviciu', form=form)


@mod.route('/setari/modifica/<srvid>', methods=['GET','POST'])
@manager_required
@login_required
def edit_service(srvid):
    """
    Used to edit a registered service
    """
    class F(ServiceForm):
        pass
    
    srv = Services.get({"_id":srvid})
    form = ServiceForm()

    if form.validate_on_submit():
        try:
            srv.populate_from_form(form)
            print request.form
            srv.authentication.value = {"db":request.form.get('authdb'),"user":request.form.get('authuser'),"pswd":request.form.get("authpass")}
            srv.save()
            flash('Datele au fost modificate!', category='alert-success')
            return redirect(url_for('services.list_services'))
        except Exception as err:
            flash('Modificarile nu pot fi salvate!', category='alert-danger')


    if srv.authentication.value:
        if srv.authentication.value['db']:
            F.authdb = StringField(label="Db autentificare")
        if srv.authentication.value['user']:
            F.authuser = StringField(label="User")
        F.authpass = StringField(label="Parola")
        F.submit = SubmitField('Salveaza')
        
    form = srv.fill_form(_form=F())
    del form.authentication
    if srv.authentication.value:
        if srv.authentication.value['db']:
            form.authdb.data = srv.authentication.value['db']
        if srv.authentication.value['user']:
            form.authuser.data = srv.authentication.value['user']
        form.authpass.data = srv.authentication.value['pswd']
        

    return render_template('services/settings/edit.html', pagetitle='Detalii serviciu', form=form)


@mod.route('/setari/sterge/<srvid>')
@manager_required
@login_required
def delete_service(srvid):
    """
    Used to delete an existing service
    """
    
    srv = Services.get({"_id":srvid})
    srv.delete()

    return redirect(request.referrer)


@mod.route('/setari/dezactiveaza/<srvid>')
@manager_required
@login_required
def deactivate_service(srvid):
    """
    Used through AJAX to deactivate a service
    """
    
    srv = Services.get({"_id":srvid})
    srv.update({"$set":{srv.active.dbfield:False}})
    
    return redirect(request.referrer)


@mod.route('/setari/activeaza/<srvid>')
@manager_required
@login_required
def activate_service(srvid):
    """
    Used through AJAX to activate an existing service
    """
    
    srv = Services.get({"_id":srvid})
    srv.update({"$set":{srv.active.dbfield:True}})
    
    return redirect(request.referrer)


@mod.route("/setari/ajax/lista", methods=['POST'])
@manager_required
@login_required
def get_results():
    """
    Used through AJAX to get datatables results
    """
    
    results = Services.to_datatables(request.form)

    for item in results["data"]:
        
        temp = item["server"]
        item["server"] = """<a href="{0}">{1}</a>""".format(url_for('services.edit_service',srvid=item["DT_RowId"]),temp)

        action_column = ""
        
        if item["active"]:
            action_column+="""<span>
                     <a href="{0}" class="btn btn-xs btn-warning"><span class="glyphicon glyphicon-eye-close" aria-hidden="true" data-toggle="tooltip" data-placement="top" title="Dezactiveaza serviciu"></span></a>
                  </span>
                  """.format(url_for('services.deactivate_service',srvid=item["DT_RowId"]))
        else:
            action_column+="""<span>
                     <a href="{0}" class="btn btn-xs btn-success"><span class="glyphicon glyphicon-eye-open" aria-hidden="true" data-toggle="tooltip" data-placement="top" title="Activeaza serviciu"></span></a>
                  </span>""".format(url_for('services.activate_service',srvid=item["DT_RowId"]))
        action_column+="""<span>
                     <a href="javascript:void(0)" onclick="DeletePage('{0}')" class="btn btn-xs btn-danger"><span class="glyphicon glyphicon-remove" aria-hidden="true" data-toggle="tooltip" data-placement="top" title="Sterge serviciu"></span></a>
                  </span>""".format(url_for("services.delete_service",srvid=item["DT_RowId"]))
                  
        item["actiuni"] = action_column

    return jsonify(results)


@mod.route('/db/home')
@login_required
def home():
    """
    Generates the homepage for the software services section
    """
    table_head = ["Server","Serviciu","Uptime","Observatii"]

    return render_template('services/list.html', pagetitle='Sumarizare statusuri db', results=url_for('services.get_datatables_results',_filter='0'),table_head=table_head)


@mod.route('/db/<db_type>')
@login_required
def dbstatus(db_type=None):
    """
    Generates a stats page for each service type
    """
    live_services = Services.get_active()
    results = REGISTERED_SERVICES[db_type]["panel"](live_services.get(db_type))

    template = 'services/detailed_%s.html' % db_type

    return render_template(template, pagetitle='Statusuri db pentru '+str(db_type).upper(), results=results)


@mod.route('/db/ajax/lista/<_filter>', methods=["POST"])
@login_required
def get_datatables_results(_filter=None):

    live_services = Services.get_active()

    stats = []
    stats_redis = REGISTERED_SERVICES['redis']["datatable"](live_services.get('redis'))
    stats_mongo = REGISTERED_SERVICES['mongo']["datatable"](live_services.get('mongo'))

    if _filter == 'mongo' and stats_mongo:
        stats = stats_mongo['data']
    elif _filter == 'redis' and stats_redis:
        stats = stats_redis['data']
    else:
        stats.extend(stats_mongo['data'])
        stats.extend(stats_redis['data'])

    output = {}
    output['draw'] = request.form['draw']
    output['data'] = stats
    output['recordsTotal'] = len(stats)
    output['recordsFiltered'] = len(stats)

    return jsonify(output)



