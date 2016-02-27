# system imports
import datetime
# framework imports
from flask import Blueprint, request, render_template, flash, redirect, url_for, session, current_app, jsonify
from flask.ext.login import login_user, logout_user, login_required, current_user
# app imports
from models import Users
from forms import UserForm, LoginForm, ResetPassForm, NewPassForm, ChangePassForm
from ..utils.mail import send_email


mod = Blueprint('users',__name__)


@mod.before_request
def before_request():
    session['menu'] = current_app.config['MENU']
    session['activemenu'] = 'utilizatori'


@mod.route('/login', methods=['GET','POST'])
def login():
    """
    Generates and handles the login for the user
    """
    form = LoginForm()

    if form.validate_on_submit():
        try:
            user = Users.get({"email":form.email.data})
            if not user.active.value:
                flash('Contul tau a expirat! Te rugam contacteaza-ne!', category='alert-danger')
                return redirect(request.referrer)
            if user.verify_password(form.password.data):
                login_user(user,form.remember_me.data)
                user.ping()
                return redirect('/')
            else:
                raise Exception('Not authorised',form.email.data)

        except Exception as err:
            print err
            flash('Parola sau adresa de email este invalida!', category='alert-danger')

    return render_template('users/login.html', pagetitle='Login',form=form,login=True, current_user=current_user)


@mod.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect('/')


@mod.route('/reseteazaparola/', methods=['GET','POST'])
def resetlink():
    """
    Generates and handles the password reset page
    """

    form = ResetPassForm()

    if form.validate_on_submit():
        try:
            user = Users.get({"email":form.email.data})
            token = user.generate_reset_token()
            send_email(user.email,'Resetare parola','users/email/passwdreset',user=user,token=token)
            flash('Parola a fost resetata! Va rugam urmati instructiunile primite pe email!',category='alert-success')
            return redirect(request.referrer)

        except Exception as err:
            flash('Adresa de email gresita!',category='alert-danger')
            return redirect(request.referrer)

    return render_template('users/login.html',pagetitle='Resetare parola',form=form,login=False)


@mod.route('/reseteaza/<email>/<token>', methods=['GET','POST'])
def resetpassword(email,token):
    """
    Handles the password reset for a given email and token
    """

    form = NewPassForm()

    if form.validate_on_submit():
        try:
            user = Users.get({"email":email})
            if user.resetpass(token):
                user.password = form.password.data
                user.save()
                flash('Parola schimbata!',category='alert-success')
                return redirect(url_for('users.login'))
                
            else:
                raise Exception

        except:
            flash('Token invalid!',category='alert-danger')
            return redirect(url_for('users.resetlink'))

    return render_template('users/login.html',pagetitle='Resetare parola',form=form,login=False)


@mod.route('/schimbaparola', methods=['GET','POST'])
@login_required
def changepswd():
    """
    Handles the change of password for the current user
    """

    form = ChangePassForm()

    if form.validate_on_submit():
        try:
            user = current_user
            print "here"
            if user.verify_password(form.oldpass.data):
                print "pass ok"
                user.password = form.newpass.data
                print user.username.value
                print form.newpass.data
                user.save()
                flash('Parola schimbata!',category='alert-success')
                return redirect(request.args.get('next') or '/home/')
            else:
                raise Exception('Not authorised',form.email.data)

        except Exception as err:
            print err
            flash('Modificarea nu poate fi facuta!', category='alert-danger')

    return render_template('users/edit.html', pagetitle='Schimba parola', form=form)


@mod.route('/home')
@login_required
def home():
    """
    Generates the homepage for the logged in user
    """

    return redirect(url_for('users.list_users'))


@mod.route('/utilizatori/lista')
@login_required
def list_users():
    """
    Generates a list of all users
    """
    return render_template('users/list.html', pagetitle='Lista Utilizatori', results=url_for('users.get_results'), table_head=Users.table_head(), columns=Users.datatables_columns())


@mod.route('/utilizatori/adauga', methods=['GET','POST'])
@login_required
def add_user():
    """
    Used to add a new user to the admin
    """

    form = UserForm()

    if form.validate_on_submit():
        try:
            user = Users()
            user.populate_from_form(form)
            send_email(user.email.value,'Resetare parola','users/email/sendpass',user=user,psw=user.random_password())
            user.save()
            flash('Utilizatorul adaugat!', category='alert-success')
            return redirect(url_for('users.list_users'))
        except Exception as err:
            flash('Utilizatorul nu poate fi adaugat!', category='alert-danger')

    return render_template('users/add.html', pagetitle='Adauga utilizator', form=form)


@mod.route('/utilizatori/modifica/<userid>', methods=['GET','POST'])
@login_required
def edit_user(userid):
    """
    Used to edit an existing user
    """
    
    user = Users.get({"_id":userid})
    form = UserForm()

    if form.validate_on_submit():
        try:
            user.populate_from_form(form)
            user.save()
            flash('Utilizatorul modificat!', category='alert-success')
            return redirect(url_for('users.list_users'))
        except Exception as err:
            print err
            flash('Modificarile nu pot fi salvate!', category='alert-danger')

    form = user.fill_form()

    return render_template('users/edit.html', pagetitle='Detalii utilizator', form=form)


@mod.route('/utilizatori/sterge/<userid>')
@login_required
def delete_user(userid):
    """
    Used to delete an existing user
    """
    
    user = Users.get({"_id":userid})
    user.delete()

    return redirect(request.referrer)


@mod.route('/utilizatori/dezactiveaza/<userid>')
@login_required
def deactivate_user(userid):
    """
    Used to deactivate a user
    """
    
    user = Users.get({"_id":userid})
    user.update({"$set":{user.active.dbfield:False}})
    
    return redirect(request.referrer)


@mod.route('/utilizatori/activeaza/<userid>')
@login_required
def activate_user(userid):
    """
    Used to activate an existing user
    """
    
    user = Users.get({"_id":userid})
    user.update({"$set":{user.active.dbfield:True}})
    
    return redirect(request.referrer)


@mod.route("/utilizatori/ajax/lista", methods=['POST'])
@login_required
def get_results():
    """
    Used through AJAX to get datatables results
    """
    results = Users.to_datatables(request.form)

    for item in results["data"]:
        
        temp = item["username"]
        item["username"] = """<a href="{0}">{1}</a>""".format(url_for('users.edit_user',userid=item["DT_RowId"]),temp)

        action_column = ""
        
        if item["active"] and str(current_user._id.value) != item["actiuni"]:
            action_column+="""<span>
                     <a href="{0}" class="btn btn-xs btn-warning"><span class="glyphicon glyphicon-user" aria-hidden="true" data-toggle="tooltip" data-placement="top" title="Dezactiveaza utilizator"></span></a>
                  </span>
                  """.format(url_for('users.deactivate_user',userid=item["DT_RowId"]))
        elif not item["active"] and str(current_user._id.value) != item["actiuni"]:
            action_column+="""<span>
                     <a href="{0}" class="btn btn-xs btn-success"><span class="glyphicon glyphicon-user" aria-hidden="true" data-toggle="tooltip" data-placement="top" title="Activeaza utilizator"></span></a>
                  </span>""".format(url_for('users.activate_user',userid=item["DT_RowId"]))
        if str(current_user._id.value) != item["actiuni"]:
            action_column+="""<span>
                     <a href="javascript:void(0)" onclick="DeletePage('{0}')" class="btn btn-xs btn-danger"><span class="glyphicon glyphicon-remove" aria-hidden="true" data-toggle="tooltip" data-placement="top" title="Sterge utilizator"></span></a>
                  </span>""".format(url_for("users.delete_user",userid=item["DT_RowId"]))

        item["actiuni"] = action_column

    return jsonify(results)

