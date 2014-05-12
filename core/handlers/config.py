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

from core.base import BaseHandler, user_required
from core.util import strip_tags
from core.models import UserProfile


class ConfigHandler(BaseHandler):
	@user_required
	def get(self):
		return self.render('app/config.html')

	@user_required
	def update(self):
		name = self.request.get('conf_name')
		value = self.request.get('conf_value')

		user_settings = self.logged.settings or {}
		user_settings[name] = value
		self.logged.settings = user_settings
		self.logged.put()

		return self.render_json({'success': True})
