# -*- coding: utf-8 -*-
'''
Created on Sept 26, 2013

@author: Rafael Nunes
'''

from google.appengine.api import channel
from google.appengine.ext.ndb import Key
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import deferred

from webapp2 import redirect_to, redirect, uri_for
from webapp2_extras import json

from core.base import BaseHandler, user_required
from core.models import Subject, Class, UserProfile, VideoComment, Notification
from core.template_filters import avatar_url, dateformat, date_to_milis


class ClassHandler(BaseHandler):
    def get(self, class_id):
    	cls = Class.get_by_id(int(class_id))
    	if not cls:
    		self.abort(404)

        upload_to = blobstore.create_upload_url('/addmaterial')
        return self.render('app/class_detail.html', cls=cls, upload_to=upload_to)

    def by_subject(self, subject_id):
    	subject = Subject.get_by_id(int(subject_id))

        if not subject:
            return self.abort(404)

    	alerts = []

    	if self.request.method == 'POST':
    		title = self.request.get('title')
    		desc = self.request.get('desc')

    		if not title:
    			alerts.append('Title field is required!')
    		else:
	    		clazz = Class(title=title, description=desc, subject=subject.key)
    			clazz.put()
    			return self.render('app/class_detail.html', cls=clazz)

    	classes = subject.get_classes()
    	return self.render('app/classes.html', classes=classes, alerts=alerts, subject=subject)

    @user_required
    def delete(self, class_id):
    	cls = Class.get_by_id(int(class_id))
    	if cls:
    		cls.key.delete()

    	return redirect_to('classes_by_subject', subject_id=cls.subject.id())

    @user_required
    def add_video(self):
        cls = self.get_object_or_404(Class, int(self.request.get('class_id', 1)))

    	title = self.request.get('vtitle')
    	video_url = self.request.get('vurl')

    	cls.add_video(title=title, url=video_url)

        deferred.defer(notify_followers_new_content, cls.subject, _queue='notify')

    	return redirect('/class/' + str(cls.key.id()) + '#video-tab')

    @user_required
    def delete_video(self):
        cls = self.get_object_or_404(Class, int(self.request.get('class_id', 1)))
        video_date = self.request.get('video_ts')

        cls.delete_video(long(video_date))

        return redirect('/class/' + str(cls.key.id()) + '#video-tab')

    @user_required
    def comment_video(self):
        comment = self.request.get('comment')
        time = self.request.get('time')
        video = self.request.get('video')

        vcomment = VideoComment(profile=self.logged.key, video_id=video, video_time=time, comment=comment)
        vcomment.put()

        return self.render_json({'success': True, 'comment': comment, 'time': time, 'id': vcomment.key.id()})

    @user_required
    def get_video_comments(self):
        video = self.request.get('video')
        comments = VideoComment.query(VideoComment.profile == self.logged.key, VideoComment.video_id == video).order(VideoComment.created_at).fetch()

        json_comments = []
        for com in comments:
            json_comments.append({
                'comment': com.comment,
                'time': com.video_time,
                'id': com.key.id(),
            })

        return self.render_json({'comments': json_comments})

    @user_required
    def delete_video_comment(self):
        cid = self.request.get('comment_id')

        comment = self.get_object_or_404(VideoComment, int(cid))
        comment.delete()

        return self.render_json({'success': True})



    @user_required
    def add_resource(self):
    	cls = Class.get_by_id(int(self.request.get('class_id')))

    	if not cls:
    		self.abort(404)

    	title = self.request.get('rtitle')
    	url = self.request.get('rurl')

    	cls.add_resource(title, url)

        deferred.defer(notify_followers_new_content, cls.subject, _queue='notify')

    	return redirect('/class/' + str(cls.key.id()) + '#additional-tab')

    @user_required
    def delete_resource(self):
        cls = self.get_object_or_404(Class, int(self.request.get('class_id', 1)))
        resource_date = self.request.get('resource_ts')

        cls.delete_resource(long(resource_date))

        return redirect('/class/' + str(cls.key.id()) + '#additional-tab')

    @user_required
    def add_comment(self):
    	cls = self.get_object_or_404(Class, int(self.request.get('class_id')))

    	text = self.request.get('comment')
    	comment = cls.add_comment(text, self.logged)

    	return self.render_json({
            'success': True,
            'avatar_url': avatar_url(self.logged, 50),
            'profile_url': uri_for('profile_by_user', profile_id=self.logged.key.id()),
            'profile_name': self.logged.full_name,
            'comment_date': dateformat(comment.created_at),
            'comment_text': comment.text,
            'comment_ts': date_to_milis(comment.created_at)
        })

    @user_required
    def delete_comment(self):
        cls = self.get_object_or_404(Class, int(self.request.get('class_id', 1)))
        comment_date = self.request.get('comment_ts')

        cls.delete_comment(long(comment_date))

        return self.render_json({'success': True })

    @user_required
    def delete_material(self):
        cls = self.get_object_or_404(Class, int(self.request.get('class_id', 1)))
        material_date = self.request.get('material_ts')

        cls.delete_material(long(material_date))

        return redirect('/class/' + str(cls.key.id()) + '#support-tab')

    @user_required
    def addmaterial_gdrive(self):
        cls = self.get_object_or_404(Class, int(self.request.get('class_id', 1)))
        file_id = self.request.get('id')
        url = self.request.get('url')
        title = self.request.get('title')
        size = self.request.get('size', 0)
        mime = self.request.get('mime')

        cls.add_gdrive_material(title, file_id, url, size, mime)

        deferred.defer(notify_followers_new_content, cls.subject, _queue='notify')
                
        self.render_json({'redirect_to': '/class/' + str(cls.key.id()) + '#support-tab'})


class MaterialHandler(blobstore_handlers.BlobstoreUploadHandler, BaseHandler, blobstore_handlers.BlobstoreDownloadHandler):
    @user_required
    def post(self):
        upload_files = self.get_uploads('mfile')
        title = self.request.get('mtitle')
        class_id = self.request.get('class_id')

        cls = Class.get_by_id(int(class_id))

        for afile in upload_files:
            cls.add_material(title, afile.key())

        return redirect('/class/' + str(cls.key.id()) + '#support-tab')

    @user_required
    def get(self):
        bkey = self.request.get('bkey')
        blobinfo = blobstore.get(bkey)

        if not blobinfo:
            self.error(404)
        else:
            self.send_blob(bkey, save_as=blobinfo.filename)


class ChatHandler(BaseHandler):
    def get(self):
        token = channel.create_channel(self.logged.email)

        return self.render('app/channel.html', token=token)

    def post(self):
        channel.send_message(self.logged.email, 'Server received %s' %self.request.get('g'))
        return


class HangoutHandler(BaseHandler):
    def get(self):
        # Set the cross origin resource sharing header to allow AJAX
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        # Print some JSON
        self.response.out.write('{"message":"Hello World!"}\n')


def notify_followers_new_content(course):
    followers = UserProfile.query(UserProfile.followed_courses == course)
    for follower in followers:
        notify = Notification(text='Novo conteúdo adicionado %s' %(course.get().title), 
            profile=follower.key, 
            ntype='icon-warning-sign'
        )
        notify.put()
