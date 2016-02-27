# framework imports
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, ValidationError
from wtforms.validators import Required, EqualTo
from ..config import Config


class UserForm(Form):

    username = StringField(label='Nume utilizator')
    email = StringField(label='Email utilizator', validators=[Required('Campul trebuie completat!')])
    permissions = SelectField(label='Permisiuni utilizator', choices=[(Config.PERMISSIONS[x],x) for x in Config.PERMISSIONS], coerce=int)
    submit = SubmitField('Salveaza')
        
    def validate_email(self,field):
        try:
            user = Users.get({"email":field.data})
            if user:
                raise ValidationError('Email este deja folosit!')
        except:
            pass


class LoginForm(Form):

    email = StringField(label='Adresa de email', validators=[Required('Campul trebuie completat!')])
    password = PasswordField(label='Parola', validators=[Required('Campul trebuie completat!')])
    remember_me = BooleanField(label='Tine-ma minte')
    submit = SubmitField('Login')


class ResetPassForm(Form):

    email = StringField(label='Email utilizator', validators=[Required('Campul trebuie completat!')])
    submit = SubmitField('Trimite')


class NewPassForm(Form):

    password = PasswordField(label='Parola noua', validators=[Required('Campul trebuie completat!')])
    pass2 = PasswordField(label='Repeta parola', validators=[Required('Campul trebuie completat!'), EqualTo('password')])
    submit = SubmitField('Salveaza')


class ChangePassForm(Form):

    oldpass = PasswordField(label='Parola veche', validators=[Required()])
    newpass = PasswordField(label='Parola noua', validators=[Required()])
    checknewpass = PasswordField(label='Parola noua', validators=[Required(),EqualTo('newpass')])
    submit = SubmitField('Salveaza')






