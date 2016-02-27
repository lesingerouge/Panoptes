# framework imports
from flask.ext.mail import Message
from flask import render_template, current_app
# app imports
from .. import mail


def send_email(to,subject,template,**kwargs):
	'''
	Helper function used to send email.
	Used only in admin application.
	'''

	if type(to) != 'list':
		recs = [to]
	else:
		recs = to
	msg = Message(subject,sender=current_app.config['MAIL_ADDRESS'],recipients=recs)
	msg.body = render_template(template + '.txt', **kwargs)
	msg.html = render_template(template + '.html', **kwargs)
	
	mail.send(msg)