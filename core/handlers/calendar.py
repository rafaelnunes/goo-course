# -*- coding: utf-8 -*-
'''
Created on Sept 26, 2013

@author: Rafael Nunes
'''
import datetime
from google.appengine.api import channel
from google.appengine.ext.ndb import Key
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

from webapp2 import redirect_to, redirect
from webapp2_extras import json

from core.base import BaseHandler, user_required
from core.models import Subject, Class, UserProfile, CalendarEvent

class CalendarHandler(BaseHandler):
	@user_required
	def get(self):
		return self.render('app/calendar.html')

	@user_required
	def add_event(self):
		course_id = self.request.get('course', 1)
		start_date = self.request.get('date')
		start_time = self.request.get('time')
		text = self.request.get('text')

		course = Subject.get_by_id(int(course_id))

		evt_date = datetime.datetime.strptime(start_date+start_time, '%Y-%m-%d%H:%M')

		cal_event = CalendarEvent(profile=self.logged.key, summary=text, start=evt_date)
		if course:
			cal_event.course = course.key
		cal_event.put()

		event = {
			'summary': text,
			'start_date': datetime.datetime.strftime(cal_event.start, '%Y-%m-%d %H:%M'),
			'id': cal_event.key.id(),
			'course': cal_event.course.id() if course else 1,
			'course_title': cal_event.course.get().title if course else '',
		}

		return self.render_json(event)

	def delete_event(self):
		event_id = self.request.get('id')

		cal_event = self.get_object_or_404(CalendarEvent, int(event_id))
		cal_event.delete()

		return self.render_json({'success': True})

	def load_events(self):
		events = CalendarEvent.query(CalendarEvent.profile == self.logged.key).fetch()

		events_json = []
		for event in events:
			events_json.append({
				'summary': event.summary,
				'start_date': datetime.datetime.strftime(event.start, '%Y-%m-%d %H:%M'),
				'id': event.key.id(),
				'course': event.course.id() if event.course else 1,
				'course_title': event.course.get().title if event.course else '',
				'className': 'label-yellow',
			})

		return self.render_json({'events': events_json})



