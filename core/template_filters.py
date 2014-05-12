# -*- coding: utf-8 -*-
'''
Created on Sept 26, 2013

@author: Rafael Nunes
'''
from google.appengine.ext import blobstore
from google.appengine.api import images

from core import util

def dateformat(value, format='%b %m at %H:%M'):
    return value.strftime(format)

def date_to_milis(date):
	return util.datetime_to_millisecond(date)


def img_resize(image, size):
	try:
		if not image:
			return None

		return images.get_serving_url(str(image), size=int(size))
	except:
		return None


def default_avatar(url):
	if not url:
		return '/assets/images/avatar2.png'

	return url

def avatar_url(profile, size):
	if not profile:
		return '/assets/images/avatar2.png'


	if profile.is_app_profile():
		if profile.avatar:
			return images.get_serving_url(profile.avatar, size=int(size))
	elif profile.is_google_profile():
		return 'https://plus.google.com/s2/photos/profile/%s?sz=%s' %(profile.gplus_user, size)
	elif profile.is_facebook_profile():
		if int(size) < 100:
			return 'https://graph.facebook.com/%s/picture?type=%s' %(profile.fcbk_user, 'small')
		if int(size) > 100 and int(size) < 200:
			return 'https://graph.facebook.com/%s/picture?type=%s' %(profile.fcbk_user, 'normal')
		else:
			return 'https://graph.facebook.com/%s/picture?type=%s' %(profile.fcbk_user, 'large')


	return '/assets/images/avatar2.png' #default avatar

def blobstore_upload_url(url):
	return blobstore.create_upload_url(url)


def get_filters():
	filters = {
		'dateformat': dateformat,
		'img_resize': img_resize,
		'blobstore_upload_url': blobstore_upload_url,
		'default_avatar': default_avatar,
		'avatar_url': avatar_url,
		'date_to_milis': date_to_milis
	}

	return filters
