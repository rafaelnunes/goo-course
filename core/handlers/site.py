# -*- coding: utf-8 -*-
'''
Created on Sept 26, 2013

@author: Rafael Nunes
'''
import logging as log 

from google.appengine.api import mail
from google.appengine.api import search
from google.appengine.ext import deferred

from webapp2 import redirect_to, redirect, uri_for

from webapp2_extras import json
from webapp2_extras.auth import InvalidAuthIdError
from webapp2_extras.auth import InvalidPasswordError
from webapp2_extras import security

from core.base import BaseHandler
from core.util import strip_tags
from core.models import UserProfile
from core import settings

class SiteHandler(BaseHandler):
	def login(self):
		if self.request.method == 'POST':
			user = self.request.get('username')
			passwd = self.request.get('passwd')
			is_remember = True if self.request.get('remember') else False

			try:
				auth_user = self.auth.get_user_by_password(user, passwd, remember=is_remember)
				return self.redirect('/dashboard', permanent=True)
			except (InvalidAuthIdError, InvalidPasswordError):
				log.info('Login failed. Wrong email or password: %s | %s' %(user, passwd))
				errors = ['Login failed. Wrong email or password!']
				return self.render('login.html', errors=errors, username=user)

			except Exception as e:
				log.info(str(e))
				errors = [str(e)]
				return self.render('login.html', errors=errors, username=user)
		else:
			if not self.auth.get_user_by_session():
				return self.render('login.html')
			else:
				return self.redirect_to('dashboard')

	def login_facebook(self):
		fb_object = json.decode(self.request.get('fb_object'))

		try:
			auth_user = self.auth.get_user_by_password(fb_object['username'], fb_object['id'], remember=True)
		except (InvalidAuthIdError, InvalidPasswordError):
			self._create_new_user(fb_object['username'], fb_object['email'], fb_object['id'], name=fb_object['first_name'], 
				last_name=fb_object['last_name'], fcbk_url=fb_object['link'], login_type=UserProfile.FACEBOOK_USER, fcbk_user=fb_object['id'])

		self.render_json({'redirect_to': uri_for('dashboard')})

	def login_gplus(self):
		gplus = json.decode(self.request.get('gplus_object'))
		try:
			auth_user = self.auth.get_user_by_password(gplus['email'], gplus['id'], remember=True)
		except (InvalidAuthIdError, InvalidPasswordError):
			self._create_new_user(gplus['email'], gplus['email'], gplus['id'], name=gplus['first_name'], 
				last_name=gplus['last_name'], gplus_url=gplus['url'], login_type=UserProfile.GOOGLE_USER, gplus_user=gplus['id'])

		self.render_json({'redirect_to': uri_for('dashboard')})

	def register(self):
		fname = self.request.get('name')
		email = self.request.get('email')
		passwd = self.request.get('passwd')

		registered = UserProfile.get_by_auth_id(email)
		if registered:
			errors = ['User "%s" already registered.' %registered.email]
			return self.render('login.html', errors=errors, username=registered.email)

		names = fname.split()
		self._create_new_user(email, email, passwd, name=names[0], last_name=' '.join(names[1:]))

		return self.redirect_to('dashboard')

	def logout(self):
		self.auth.unset_session()
		self.redirect('/')

	def _create_new_user(self, username, email, passwd, **user_attributes):
		user_data = self.user_model.create_user(username, [], 
			email_address=email,password_raw=passwd, verified=False, **user_attributes)
		
		# If not user_data, create failed
		user = user_data[1]
		if not user:
			raise Exception('User not created')

		self.auth.set_session(self.auth.store.user_to_dict(user), remember=True)

		# TODO send welcome email

		deferred.defer(index_profile, user, _queue='profileIndex')

	def forgot_password(self):
		email = self.request.get("email")

		user = UserProfile.get_by_auth_id(email)

		if not user:
			return self.render_json({'success': False, 'title': 'Sorry.', 'message': 'Nenhum usuário com o email "%s" foi encontrado.' %email})

		new_password = security.generate_random_string(length=8)
		user.set_password(new_password)
		print 'New Password ======================> ', new_password

		user.put()

		deferred.defer(send_forgot_password_email, user=user, new_passwd=new_password, _queue='sendEmail') #TODO improve this queue params/conf

		return self.render_json({'success': True, 'title': 'Senha reiniciada.', 'message': 'Enviamos um email para %s com sua nova senha' %email})

	def change_password(self):
		newpass = self.request.get("newpass")		
		user = self.logged

		user.set_password(str(newpass))
		user.put()

		return self.render_json({'success': True})

	def not_found(self):
		return self.render('app/404.html')

	def about(self):
		return self.render('about.html')


def index_profile(user):
	try:
		doc = search.Document(
		doc_id = str(user.key.id()),
		fields=[
		   search.TextField(name='first_name', value=user.name),
		   search.TextField(name='last_name', value=user.last_name),
		   search.TextField(name='email', value=user.email),
		])

		index = search.Index(name="profileIndex")
		index.put(doc)
	except search.Error:
		# TODO send admin email
		log.exception('Error indexing subject[%s]' %user.key.id())	


def send_forgot_password_email(user, new_passwd):
	message = mail.EmailMessage(sender=settings.EMAIL_SENDER,
                            subject="Your new password")

	message.to = "%s <%s>" %(user.full_name, user.email)
	message.body = """
	Olá %s:

	Você solicitou que sua senha fosse reiniciada.
	Sua nova senha é: %s

	Qualquer problema ou dúvida, entre em contato conosco.

	Obrigado,
	""" %(user.name, new_passwd)

	message.send()