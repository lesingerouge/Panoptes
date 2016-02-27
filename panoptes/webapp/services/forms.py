# framework imports
from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, SubmitField, SelectField, ValidationError
from wtforms.validators import Required, EqualTo
#app imports
from ..config import Config


class ServiceForm(Form):

    server = StringField(label="IP server", validators=[Required('Campul trebuie completat!')])
    port = StringField(label="Port server", validators=[Required('Campul trebuie completat!')])
    service_type = SelectField(label="Tip serviciu", choices=[(x,x.upper()) for x in Config.SERVICE_TYPES])
    authentication = SelectField(label="Autentificare", choices=[(False,'NU'),(True,'DA')], coerce=bool)
    submit = SubmitField('Salveaza')
