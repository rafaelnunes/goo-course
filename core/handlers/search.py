# -*- coding: utf-8 -*-
'''
Created on Sept 26, 2013

@author: Rafael Nunes
'''
import logging as log
from webapp2 import redirect_to, redirect
from google.appengine.api import search

from core.base import BaseHandler, user_required
from core.models import UserProfile, Subject
from core.template_filters import dateformat, avatar_url

class SearchHandler(BaseHandler):
	@user_required
	def get(self):
		return self.render('app/search.html')

	@user_required
	def people(self):
		return self.render('app/search.html', search_people=True)

	@user_required
	def search_subject(self):
		q = self.request.get('q', '')
		index = search.Index(name='subjectIndex')
		query = index.search(q)

		subjects = [Subject.get_by_id(int(result.doc_id)) for result in query.results]
		subjects = [sub for sub in subjects if sub != None]

		return self.render('app/search_result.html', subjects=subjects, search_term=q)

	@user_required
	def search_people(self):
		qu = self.request.get('q', '')
		index = search.Index(name='profileIndex')
		query = index.search(qu)

		profiles = [UserProfile.get_by_id(int(result.doc_id)) for result in query.results]
		return self.render('app/search_people_result.html', profiles=profiles, search_term=qu)

	@user_required
	def courses_by(self):
		profile_id = self.request.get('profile')

		profile = self.get_object_or_404(UserProfile, int(profile_id))

		return self.render('app/search_result.html', subjects=profile.get_subjects())

	@user_required
	def followed_by(self):
		profile_id = self.request.get('profile')

		profile = self.get_object_or_404(UserProfile, int(profile_id))

		return self.render('app/search_result.html', subjects=profile.get_followed_courses())