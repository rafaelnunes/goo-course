# -*- coding: utf-8 -*-
'''
Created on Sept 26, 2013

@author: Rafael Nunes
'''
import logging as log

from google.appengine.ext import deferred
from google.appengine.api import search
from google.appengine.api import mail

from webapp2 import uri_for

from core.base import BaseHandler, user_required
from core.models import Subject, UserProfile, Notification
from core import settings


class SubjectHandler(BaseHandler):
    @user_required
    def get(self):
        subjects = []
        
        if self.logged:
    	   subjects = self.logged.get_subjects()

        return self.render('app/subjects.html', subjects=subjects)

    @user_required
    def post(self):
    	title = self.request.get('title')
        desc = self.request.get('desc')

    	if not title:
            return self.render_json({'success': False, 'message':'Campo Titulo obrigatório!'})
        else:
            subject = Subject(title=title, description=desc, owner=self.logged.key)
            subject.put()

            deferred.defer(index_subject, subject, _queue='subjectIndex')

            return self.render_json({'success': True, 'redirect': uri_for('classes_by_subject', subject_id=subject.key.id())})

    @user_required
    def get_courses(self):
        courses = self.logged.get_subjects()

        courses_response = []
        for course in courses:
            courses_response.append({
                'id': course.key.id(),
                'title': course.title,
                'description': course.description,
                'owner': course.owner.id(),
            })

        return self.render_json({'courses': courses_response})

    @user_required
    def delete_course(self):
        course_id = self.request.get('course_id')

        course = self.get_object_or_404(Subject, int(course_id))
        course.delete()

        return self.render_json({'success': True})

    @user_required
    def follow_course(self):
        course_id = self.request.get('course_id', 0)

        course = self.get_object_or_404(Subject, int(course_id))

        if course.owner == self.logged.key:
            return self.render_json({'success': False})

        self.logged.followed_courses.append(course.key)
        self.logged.put()

        deferred.defer(notify_follow, course, self.logged, _queue='notify')

        return self.render_json({'success': True})

    @user_required
    def unfollow_course(self):
        course_id = self.request.get('course_id', 0)

        course = self.get_object_or_404(Subject, int(course_id))

        self.logged.followed_courses = [sub for sub in self.logged.followed_courses if sub != course.key] # TODO method on UserProfile class
        self.logged.put()

        return self.render_json({'success': True})

    @user_required
    def invite_friend(self):
        course_id = self.request.get('course_id', 0)
        friend = self.request.get('email', '')

        course = self.get_object_or_404(Subject, int(course_id))

        mail.send_mail(settings.EMAIL_SENDER, friend, '%s te convidou para acompompanhar um curso' %self.logged.get_name_or_email(), 
            """
                Olá,
                Seu amigo %s recomendou para você o curso '%s'. Se você estiver interessado, clique no link a seguir para conhecer mais: %s
            """ %(self.logged.get_name_or_email(), course.title, settings.HOST_NAME + course.public_url()),
        )

        return self.render_json({'success': True})



def index_subject(subject):
    try:
        doc = search.Document(
        doc_id = str(subject.key.id()),
        fields=[
           search.TextField(name='title', value=subject.title),
           search.TextField(name='description', value=subject.description),
           search.TextField(name='owner', value=str(subject.key.id())),
        ])

        index = search.Index(name="subjectIndex")
        index.put(doc)
    except search.Error:
        # TODO send admin email
        log.exception('Error indexing subject[%s]' %subject.key.id())


def notify_follow(course, user):
    notify = Notification(text='%s começou a seguir o curso %s' %(user.full_name, course.title), 
        profile=course.owner, 
        ntype='icon-warning-sign'
    )
    notify.put()
