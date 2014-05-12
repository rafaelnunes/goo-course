# -*- coding: utf-8 -*-
'''
Created on Oct 3, 2013

@author: Rafael Nunes
'''
import time
from urlparse import urlparse, parse_qs


from google.appengine.ext import ndb
from google.appengine.ext import blobstore

from webapp2 import uri_for
from webapp2_extras.appengine.auth.models import User as GAEUser
from webapp2_extras import security

from core.base import BaseModel
from core import util


class UserProfile(GAEUser):
	APP_USER = 0
	GOOGLE_USER = 1
	FACEBOOK_USER = 2

	TYPE_STUDENT = 0
	TYPE_ADMIN = 1
	TYPE_STAFF = 2

	TYPE_CHOICES = {
		TYPE_STUDENT: 'Estudante',
		TYPE_ADMIN: 'Admin',
		TYPE_STAFF: 'Staff',
	}

	gplus_user = ndb.StringProperty()
	fcbk_user = ndb.StringProperty()

	login_type = ndb.IntegerProperty(default=APP_USER)
	avatar = ndb.BlobKeyProperty()
	about = ndb.TextProperty()
	website = ndb.StringProperty()
	fcbk_url = ndb.StringProperty()
	tw_url = ndb.StringProperty()
	gplus_url = ndb.StringProperty()

	followed_courses = ndb.KeyProperty(kind='Subject', repeated=True)

	settings = ndb.JsonProperty()

	user_type = ndb.IntegerProperty(default=TYPE_STUDENT)

	def set_password(self, raw_password):
		self.password = security.generate_password_hash(raw_password, length=12)
 
  	@classmethod
  	def get_by_auth_token(cls, user_id, token, subject='auth'):
	    """Returns a user object based on a user ID and token.
	 
	    :param user_id:
	        The user_id of the requesting user.
	    :param token:
	        The token string to be verified.
	    :returns:
	        A tuple ``(User, timestamp)``, with a user object and
	        the token timestamp, or ``(None, None)`` if both were not found.
	    """
	    token_key = cls.token_model.get_key(user_id, subject, token)
	    user_key = ndb.Key(cls, user_id)
	    # Use get_multi() to save a RPC call.
	    valid_token, user = ndb.get_multi([token_key, user_key])

	    if valid_token and user:
	        timestamp = int(time.mktime(valid_token.created.timetuple()))
	        return user, timestamp
	 
	    return None, None

	@property
	def email(self):
		return self.email_address

	@property
	def short_about(self):
		return self.about or ""

	@property
	def full_name(self):
		return '%s %s' %(self.name, self.last_name)

	@property
	def short_about(self):
		short = ''
		if self.about:
			short = self.about[:50] + '...'

		return short

	def get_name_or_email(self):
		if not self.name:
			return self.email_address

		return self.name

	def is_app_profile(self):
		return self.login_type == self.APP_USER

	def is_google_profile(self):
		return self.login_type == self.GOOGLE_USER

	def is_facebook_profile(self):
		return self.login_type == self.FACEBOOK_USER

	def get_subjects(self):
		return Subject.query(Subject.owner == self.key).fetch()

	def get_followed_courses(self):
		if not self.followed_courses or not self.followed_courses[0]:
			return [] 

		return [k.get() for k in self.followed_courses if k.get()  and k.get() not in self.get_subjects()]

	def get_my_courses(self):
		return self.get_subjects() + self.get_followed_courses()

	def is_following(self, subject):
		return subject.key in self.followed_courses

	def has_setting(self, name):
		settings = self.settings or {}
		return (name in settings.keys()) and settings[name] == 'true'

	def get_setting(self, setting_name):
		if not self.settings:
			return None

		return self.settings.get(setting_name, None)

	def is_admin(self):
		return self.user_type == self.TYPE_ADMIN

	def is_staff(self):
		return self.user_type == self.TYPE_STAFF

	def is_student(self):
		return self.user_type == self.TYPE_STUDENT

class Subject(BaseModel):
	TYPE_FREE = 1

	payment_type = ndb.IntegerProperty(default=TYPE_FREE)
	title = ndb.StringProperty()
	description = ndb.TextProperty()
	owner = ndb.KeyProperty(kind=UserProfile)

	def get_classes(self):
		return Class.query(Class.subject == self.key).order(Class.created_at).fetch()

	def is_admin(self, profile):
		if not profile:
			return False

		return self.owner == profile.key

	def public_url(self):
		return '/classes/%s' %self.key.id()

	def __unicode__(self):
		return self.title


class Video(BaseModel):
	title = ndb.StringProperty()
	url = ndb.StringProperty()
	created_at = ndb.DateTimeProperty(auto_now_add=True)

	def get_video_id(self):
		url = urlparse(self.url)
		
		if 'youtube' in url.netloc:
			qs_dict = parse_qs(urlparse(self.url).query)
			video_id = qs_dict.get('v', None)
			return video_id[0] if video_id else ''
		elif 'youtu.be' in url.netloc:
			return url.path[1:]


class SupportMaterial(ndb.Expando):
	TYPE_BLOBSTORE = 1
	TYPE_GDRIVE = 2

	title = ndb.StringProperty()
	blob_key = ndb.BlobKeyProperty()
	created_at = ndb.DateTimeProperty(auto_now_add=True)
	material_source = ndb.IntegerProperty(default=TYPE_BLOBSTORE)

	#TODO more content types
	CTYPE_ICON = {
		'application/pdf': 'images/gallery/pdf_icon.png',
		'image/jpeg': 'images/gallery/jpeg_icon.png',
		'text/plain': 'images/gallery/txt_icon.png',
		'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'images/gallery/xls_icon.png',
		'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'images/gallery/doc_icon.png',
		'application/zip': 'images/gallery/zip_icon.png',
		'application/vnd.google-apps.spreadsheet': 'images/gallery/gsheets_icon.png',
		'application/vnd.google-apps.document': 'images/gallery/gdoc_icon.png',
		'application/vnd.google-apps.form': 'images/gallery/gform_icon.png',
		'application/vnd.google-apps.presentation': 'images/gallery/gpresent_icon.png',
	}

	def get_icon(self):
		if self.material_source == self.TYPE_BLOBSTORE:
			ctype = blobstore.get(self.blob_key).content_type
		else:
			ctype = self.mime_type
			print ctype

		return self.CTYPE_ICON.get(ctype, 'images/gallery/generic_icon.png')

	def get_size(self):
		if self.material_source == self.TYPE_BLOBSTORE:
			bytes = blobstore.get(self.blob_key).size
		else:
			bytes = float(self.size) or 0.0

		def sizeof_fmt(num):
		    for x in ['bytes','KB','MB','GB','TB']:
		        if num < 1024.0:
		            return "%3.1f %s" % (num, x)
		        num /= 1024.0

		return sizeof_fmt(bytes) if bytes else None

	def get_download_url(self):
		if self.material_source == self.TYPE_BLOBSTORE:
			return uri_for('get_material') + '?bkey=%s' % self.blob_key

		return self.url


class ClassResource(BaseModel):
	title = ndb.StringProperty()
	url = ndb.StringProperty()
	created_at = ndb.DateTimeProperty(auto_now_add=True)


class ClassComment(BaseModel):
	text = ndb.TextProperty()
	profile_key = ndb.KeyProperty()
	created_at = ndb.DateTimeProperty(auto_now_add=True)

	@property
	def profile(self):
		return self.profile_key.get()

	def can_delete(self, profile):
		if not profile:
			return False

		return self.profile_key == profile.key


class Class(BaseModel):
	subject = ndb.KeyProperty(kind=Subject)
	title = ndb.StringProperty()
	description = ndb.TextProperty()
	created_at = ndb.DateTimeProperty(auto_now_add=True)

	videos = ndb.LocalStructuredProperty(Video, repeated=True)
	materials = ndb.LocalStructuredProperty(SupportMaterial, repeated=True)
	resources = ndb.LocalStructuredProperty(ClassResource, repeated=True)
	comments = ndb.LocalStructuredProperty(ClassComment, repeated=True)


	def add_video(self, title, url):
		self.videos.append(Video(title=title, url=url))
		self.put()

	def delete_video(self, video_ts):
		self.videos = [video for video in self.videos if util.datetime_to_millisecond(video.created_at) != video_ts]
		self.put()

	def add_material(self, title, bkey):
		self.materials.append(SupportMaterial(title=title, blob_key=bkey))
		self.put()

	def add_gdrive_material(self, title, file_id, url, size, mime):
		material = SupportMaterial(title=title, material_source=SupportMaterial.TYPE_GDRIVE)
		material.file_id = file_id
		material.url = url
		material.size = size
		material.mime_type = mime

		self.materials.append(material)
		self.put()

	def delete_material(self, mat_ts):
		material = [mat for mat in self.materials if util.datetime_to_millisecond(mat.created_at) == mat_ts]

		self.materials = [mat for mat in self.materials if util.datetime_to_millisecond(mat.created_at) != mat_ts]
		self.put()

		#TODO remove with taskqueue
		if material[0].material_source == material[0].TYPE_BLOBSTORE:
			blobstore.delete(material[0].blob_key)

	def add_resource(self, title, url):
		self.resources.append(ClassResource(title=title, url=url))
		self.put()

	def delete_resource(self, resource_ts):
		self.resources = [resource for resource in self.resources if util.datetime_to_millisecond(resource.created_at) != resource_ts]
		self.put()

	def add_comment(self, comment, profile):
		comment = ClassComment(text=comment, profile_key=profile.key)
		self.comments.append(comment)
		self.put()

		return comment

	def delete_comment(self, comment_ts):
		self.comments = [comment for comment in self.comments if util.datetime_to_millisecond(comment.created_at) != comment_ts]
		self.put()

	def is_admin(self, profile):
		return self.subject.get().is_admin(profile)

	def get_events(self):
		return CalendarEvent.query(CalendarEvent.course == self.subject).fetch()


class Notification(BaseModel):
	text = ndb.StringProperty()
	ntype = ndb.StringProperty()
	created_at = ndb.DateTimeProperty(auto_now_add=True)
	profile = ndb.KeyProperty(kind=UserProfile)


class InboxMessage(BaseModel):
	STATUS_UNREAD = 0
	
	subject = ndb.StringProperty()
	text = ndb.TextProperty()
	sender = ndb.KeyProperty(kind=UserProfile)
	to = ndb.KeyProperty(kind=UserProfile)
	created_at = ndb.DateTimeProperty(auto_now_add=True)
	status = ndb.IntegerProperty(default=STATUS_UNREAD)


class VideoComment(BaseModel):
	video_id = ndb.StringProperty()
	video_time = ndb.StringProperty()
	comment = ndb.StringProperty()
	profile = ndb.KeyProperty(kind=UserProfile)
	created_at = ndb.DateTimeProperty(auto_now_add=True)

class CalendarEvent(BaseModel):
	course = ndb.KeyProperty(kind=Subject)
	profile = ndb.KeyProperty(kind=UserProfile)
	start = ndb.DateTimeProperty()
	gevent_id = ndb.StringProperty()
	summary = ndb.StringProperty()


