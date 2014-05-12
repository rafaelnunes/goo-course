# -*- coding: utf-8 -*-
'''
Created on Sept 26, 2013

@author: Rafael Nunes
'''
from core.base import BaseHandler, user_required
from core.models import Subject, UserProfile

class DashboardHandler(BaseHandler):
	@user_required
	def home(self):
			subjects = self.logged.get_followed_courses()
			most_followed = Subject.query().fetch()

			return self.render('app/dashboard.html', subjects=subjects, most_followed=most_followed)