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
from core.models import UserProfile, Notification

class ProfileHandler(BaseHandler):
	@user_required
	def get(self):
		profile = self.logged
		can_edit = True

		return self.render('app/profile.html', profile=profile, can_edit=can_edit)

	def profile_by_user(self, profile_id):
		profile = UserProfile.get_by_id(int(profile_id))

		if not profile:
			self.abort(404)
		
		can_edit = self.logged == profile

		return self.render('app/profile.html', profile=profile, can_edit=can_edit)

	@user_required
	def post(self):
		attr_name = self.request.get('name')
		user = self.logged
		setattr(user, attr_name, self.request.get('value'))
		user.put()

		return self.render_json({'pk': self.logged.key.id()})

	@user_required
	def get_notifications(self):
		notifications = Notification.query(Notification.profile==self.logged.key).order(-Notification.created_at).fetch(5)

		return self.render_json({'notifications': [n.to_dict() for n in notifications]})

	def add_notification(self):
		notify = Notification(text=self.request.get('text'), profile=self.logged.key, ntype='icon-comment')
		notify.put()

		return self.render_json({'success': True})




class AvatarHandler(blobstore_handlers.BlobstoreUploadHandler, BaseHandler):
    @user_required
    def post(self):
        upload_files = self.get_uploads('avatar')

        profile = self.logged

        if upload_files:
	        profile.avatar = upload_files[0].key()
	        profile.put()

	        # TODO Task queue remove old avatar

        return self.render_json({
        	'status': 'OK',
        	'url': images.get_serving_url(profile.avatar),
        })

    @user_required
    def get(self):
    	return self.send_blob()
