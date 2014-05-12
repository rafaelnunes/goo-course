# -*- coding: utf-8 -*-
'''
Created on Sept 26, 2013

@author: Rafael Nunes
'''
import webapp2
import logging as log

from google.appengine.ext import ndb

from webapp2_extras import jinja2, sessions, auth, json
from webapp2 import redirect_to

import settings


def jinja_factory(app):
            """
                Method for attaching aditional globals/filters to jinja rendering
            """
            j = jinja2.Jinja2(app)
            j.environment.globals.update({
                'uri_for': webapp2.uri_for,
                'settings': settings,
            })

            return j


def user_required(handler):
    """
    Decorator that checks if there's a user associated with the current session.
    Will also fail if there's no session present.
    """
    def check_login(self, *args, **kwargs):
        auth = self.auth
        if not auth.get_user_by_session():
            return redirect_to('login')
        else:
            return handler(self, *args, **kwargs)

    return check_login

class BaseHandler(webapp2.RequestHandler):
        @webapp2.cached_property
        def jinja2(self):
            j2 = jinja2.get_jinja2(factory=jinja_factory, app=self.app)
            return j2

        def render_str(self, filename, **template_args):
            ctx = {'logged': self.logged}
            ctx.update(template_args)

            return self.jinja2.render_template(filename, **ctx)
            
        def render(self, filename, **template_args):
            ctx = {'logged': self.logged, 'use_angular': filename in settings.TEMPLATE_USING_ANGULAR}
            ctx.update(template_args)

            self.response.write(self.jinja2.render_template(filename, **ctx))

        def render_json(self, obj):
            self.response.headers['Content-Type'] = 'application/json' 
            self.response.out.write(json.encode(obj))

        def dispatch(self):
            self.session_store = sessions.get_store(request=self.request)

            try:
                return  webapp2.RequestHandler.dispatch(self)
            finally:
                self.session_store.save_sessions(self.response)

        @webapp2.cached_property
        def auth(self):
            """Shortcut to access the auth instance as a property."""
            return auth.get_auth()

        @webapp2.cached_property
        def user_info(self):
            return self.auth.get_user_by_session()

        @webapp2.cached_property
        def session(self):
            return self.session_store.get_session(backend="datastore")

        @webapp2.cached_property
        def logged(self):
            u = self.user_info
            return self.user_model.get_by_id(u['user_id']) if u else None

        @webapp2.cached_property
        def user_model(self):
            return self.auth.store.user_model

        def handle_exception(self, exception, debug):
		    # Log the error
            log.exception(exception)

            if isinstance(exception, webapp2.exc.HTTPNotFound):
                self.render('app/404.html')

        def get_object_or_404(self, cls, object_id, parent=None):
            instance = cls.get_by_id(object_id, parent=parent)
            if not instance:
                return self.abort(404)

            return instance


def handle_404(request, response, exception):
    return webapp2.redirect_to('not_found')


class BaseModel(ndb.Model):
    def to_dict(self):
        return dict([(p, unicode(getattr(self, p))) for p in self._properties if p  != 'owner'])

    def put_async(self):
        ndb.put_async(self)

    def delete(self):
        self.key.delete()
