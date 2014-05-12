# -*- coding: utf-8 -*-
'''
Created on Sept 26, 2013

@author: Rafael Nunes
'''
import logging as log


from core.base import BaseHandler, user_required
from core.models import Subject

class APIHandler(BaseHandler):

	def get_courses(self):
		all_courses = Subject.query().fetch()

		return self.render_json({'success': True, 'courses': [course.to_dict() for course in all_courses]})