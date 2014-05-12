# -*- coding: utf-8 -*-
'''
Created on Sept 26, 2013

@author: Rafael Nunes
'''
import logging as log
from webapp2 import redirect_to, redirect
from google.appengine.api import images
from google.appengine.ext.webapp import blobstore_handlers

from core.base import BaseHandler, user_required
from core.models import UserProfile, InboxMessage
from core.template_filters import dateformat, avatar_url

class InboxHandler(BaseHandler):
	
	@user_required
	def get(self):
		messages = InboxMessage.query(InboxMessage.to == self.logged.key).fetch()

		return self.render('app/inbox.html', messages=messages)

	@user_required
	def get_recent_messages(self):
		recent = InboxMessage.query(InboxMessage.to == self.logged.key).fetch(5)

		messages = []
		for msg in recent:
			dict_msg = {
				'subject': msg.subject,
				'sender': msg.sender.get().full_name,
				'date': dateformat(msg.created_at),
				'avatar': avatar_url(msg.sender.get(), '20')
			}
			messages.append(dict_msg)

		return self.render_json({'success': True, 'messages': messages})

	@user_required
	def send_message(self):
		to = self.request.get('message_to')
		text = self.request.get('message_text')
		subject = self.request.get('message_subject')

		profile_to = self.get_object_or_404(UserProfile, int(to))

		message = InboxMessage(sender=self.logged.key, to=profile_to.key, subject=subject, text=text)
		message.put()

		return self.render_json({'success': True })

	@user_required
	def view_message(self):
		message_id = self.request.get('message_id', 1)

		msg = self.get_object_or_404(InboxMessage, int(message_id))

		dict_msg = {
				'subject': msg.subject,
				'sender': msg.sender.get().full_name,
				'sender_id': msg.sender.get().key.id(),
				'date': dateformat(msg.created_at),
				'avatar': avatar_url(msg.sender.get(), '35'),
				'text': msg.text,
				'id': msg.key.id()
			}

		return self.render_json({'success': True, 'message': dict_msg})

	@user_required
	def delete_message(self):
		message_id = self.request.get('message_id')

		message = self.get_object_or_404(InboxMessage, int(message_id))
		message.delete()
		
		return self.redirect_to('inbox')