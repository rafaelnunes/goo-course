# -*- coding: utf-8 -*-
'''
Created on Sept 26, 2013

@author: Rafael Nunes
'''


import webapp2

from core.page_handlers import *
from core.handlers import dashboard, subjects, classes, site, profile, calendar, inbox, search, config, api
from core.base import handle_404
from core.template_filters import get_filters

routes = [('/', IndexPage),
	webapp2.Route('/dashboard', handler=dashboard.DashboardHandler, handler_method='home', name='dashboard'),
	webapp2.Route('/about', handler=site.SiteHandler, handler_method='about', name='about'),


	webapp2.Route(r'/login', handler=site.SiteHandler, handler_method='login', name='login'),
	webapp2.Route(r'/login_fb', handler=site.SiteHandler, handler_method='login_facebook', name='login_facebook'),
	webapp2.Route(r'/login_gplus', handler=site.SiteHandler, handler_method='login_gplus', name='login_gplus'),
	webapp2.Route(r'/logout', handler=site.SiteHandler, handler_method='logout', name='logout'),
	webapp2.Route(r'/register', handler=site.SiteHandler, handler_method='register', name='register', methods= ['POST']),
	webapp2.Route(r'/not-found', handler=site.SiteHandler, handler_method='not_found', name='not_found'),
	webapp2.Route(r'/forgot-password', handler=site.SiteHandler, handler_method='forgot_password', name='forgot_password'),
	webapp2.Route(r'/change-passwd', handler=site.SiteHandler, handler_method='change_password', name='change-passwd'),

	
	
	webapp2.Route(r'/class/<class_id:\d+>', handler=classes.ClassHandler, name='class_by_id'),
	webapp2.Route(r'/class/<class_id:\d+>/delete', handler=classes.ClassHandler, handler_method='delete', name='delete_class'),
	webapp2.Route(r'/classes/<subject_id:\d+>', handler=classes.ClassHandler, handler_method='by_subject', name='classes_by_subject'),
	webapp2.Route(r'/addvideo', handler=classes.ClassHandler, handler_method='add_video', name='add_video'),
	webapp2.Route(r'/delete-video', handler=classes.ClassHandler, handler_method='delete_video', name='delete-video'),
	webapp2.Route(r'/comment-video', handler=classes.ClassHandler, handler_method='comment_video', name='comment-video'),
	webapp2.Route(r'/get-video-comments', handler=classes.ClassHandler, handler_method='get_video_comments', name='get-video-comments'),
	webapp2.Route(r'/delete-video-comment', handler=classes.ClassHandler, handler_method='delete_video_comment', name='delete_video_comment'),
	webapp2.Route(r'/addmaterial', handler=classes.MaterialHandler, name='add_material'),
	webapp2.Route(r'/addmaterial_gdrive', handler=classes.ClassHandler, handler_method='addmaterial_gdrive', name='addmaterial-gdrive'),

	webapp2.Route(r'/getmaterial', handler=classes.MaterialHandler, name='get_material'),
	webapp2.Route(r'/delete-material', handler=classes.ClassHandler, handler_method='delete_material', name='delete-material'),
	webapp2.Route(r'/addresource', handler=classes.ClassHandler, handler_method='add_resource', name='add_resource'),
	webapp2.Route(r'/delete-resource', handler=classes.ClassHandler, handler_method='delete_resource', name='delete-resource'),
	webapp2.Route(r'/addcomment', handler=classes.ClassHandler, handler_method='add_comment', name='add_comment'),
	webapp2.Route(r'/delete-comment', handler=classes.ClassHandler, handler_method='delete_comment', name='delete-comment'),


	webapp2.Route(r'/subjects', handler=subjects.SubjectHandler, name='subjects'),
	webapp2.Route(r'/get-courses', handler=subjects.SubjectHandler, handler_method='get_courses', name='get-courses'),
	webapp2.Route(r'/follow-course', handler=subjects.SubjectHandler, handler_method='follow_course', name='follow_course'),
	webapp2.Route(r'/unfollow-course', handler=subjects.SubjectHandler, handler_method='unfollow_course', name='unfollow_course'),
	webapp2.Route(r'/delete-course', handler=subjects.SubjectHandler, handler_method='delete_course', name='delete_course'),
	webapp2.Route(r'/invite-friend', handler=subjects.SubjectHandler, handler_method='invite_friend', name='invite_friend'),


	webapp2.Route(r'/profile', handler=profile.ProfileHandler, name='profile'),
	webapp2.Route(r'/profile/<profile_id:\d+>', handler=profile.ProfileHandler, handler_method='profile_by_user', name='profile_by_user'),
	webapp2.Route(r'/profile/avatar', handler=profile.AvatarHandler, name='profile_avatar'),
	webapp2.Route(r'/notifications', handler=profile.ProfileHandler, handler_method='get_notifications', name='profile_notifications'),
	webapp2.Route(r'/addnotification', handler=profile.ProfileHandler, handler_method='add_notification', name='add_notification'),

	webapp2.Route(r'/calendar', handler=calendar.CalendarHandler, name='calendar'),
	webapp2.Route(r'/calendar/add', handler=calendar.CalendarHandler, handler_method='add_event', name='calendar_add'),
	webapp2.Route(r'/calendar/delete', handler=calendar.CalendarHandler, handler_method='delete_event', name='calendar_delete'),
	webapp2.Route(r'/calendar/events', handler=calendar.CalendarHandler, handler_method='load_events', name='calendar_events'),


	webapp2.Route(r'/inbox', handler=inbox.InboxHandler, name='inbox'),
	webapp2.Route(r'/inbox/recent', handler=inbox.InboxHandler, handler_method='get_recent_messages', name='inbox_recent'),
	webapp2.Route(r'/send-message', handler=inbox.InboxHandler, handler_method='send_message', name='send_message'),
	webapp2.Route(r'/view-message', handler=inbox.InboxHandler, handler_method='view_message', name='view_message'),
	webapp2.Route(r'/delmessage', handler=inbox.InboxHandler, handler_method='delete_message', name='delete_message'),

	webapp2.Route(r'/search', handler=search.SearchHandler, name='search'),
	webapp2.Route(r'/people', handler=search.SearchHandler, handler_method='people', name='people'),
	webapp2.Route(r'/search/subject', handler=search.SearchHandler, handler_method='search_subject', name='search_subject'),
	webapp2.Route(r'/search/people', handler=search.SearchHandler, handler_method='search_people', name='search_people'),
	webapp2.Route(r'/followed_by', handler=search.SearchHandler, handler_method='followed_by', name='followed_by'),
	webapp2.Route(r'/courses_by', handler=search.SearchHandler, handler_method='courses_by', name='courses_by'),


	webapp2.Route('/settings', handler=config.ConfigHandler, name='load_settings'),
	webapp2.Route('/settings/update', handler=config.ConfigHandler, handler_method='update', name='update_settings'),

	webapp2.Route('/api/courses', handler=api.APIHandler, handler_method='get_courses', name='api_courses'),

]

myconfig = {
	'webapp2_extras.auth': {
    'user_model': 'core.models.UserProfile',
    'user_attributes': ['name', 'email_address'],
  },
  'webapp2_extras.sessions': {
    'secret_key': 'YOUR_SECRET_KEY' #TODO change secret key
  }
}

myconfig['webapp2_extras.jinja2'] =  {'template_path': ['templates'],
                                      'filters': get_filters()}

app = webapp2.WSGIApplication(routes, debug=True, config = myconfig)
app.error_handlers[404] = handle_404