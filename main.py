#!/usr/bin/env python
#
# Copyright 2013 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import jinja2
import os
import webapp2

from google.appengine.api import users
#from google.appengine.ext import webapp

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


TOPICS = ('Medical Innovations', 'Programming Languages', 'Web Technologies', 'Movie Making')
CITIES=('London', 'Chicago', 'San Francisco', 'Paris')


"""
class _BaseHandler(webapp2.RequestHandler):
  def initialize(self, request, response):
    super(_BaseHandler, self).initialize(request, response)
    self.user = ________________________
    if self.user:
      self.template_values = {
          'user': _________,
          'is_admin': _____________________________,
          'logout_url': ____________________________}
    else:
      self.template_values = {'login_url': ________________________________________}
"""

class DeveloperPage(webapp2.RequestHandler):
  def get(self):
    template = jinja_environment.get_template('developer.template')
    self.response.out.write(template.render())


class ListConferencesPage(webapp2.RequestHandler):
  def get(self):
    template = jinja_environment.get_template('list_conferences.template')
    self.response.out.write(template.render())


class ScheduleConferencePage(webapp2.RequestHandler):
  def get(self):
    template = jinja_environment.get_template('schedule_conference.template')
    self.response.out.write(template.render())


class UserProfilePage(webapp2.RequestHandler):
  def get(self):
    template = jinja_environment.get_template('user_profile.template')
    self.response.out.write(template.render())


class SaveUserProfile(webapp2.RequestHandler):
  def get(self):
    # If a user come to this page as a GET, redirect to the user profile page
    self.redirect('/userprofile')

  def post(self):
    #Currently we are redirecting back to the UserProfilePage with a 
    #self.redirect('/userprofile')

    #Fill in the blanks withe the appropriate data to complete the post
    #method and then remove the code from the docstring.

    """
    # get person_name, topics, notification_email from the form.
    person_name = self.request.get('___________')
    topics = self.request.get_all('______')
    notification_email = self.request.get('__________________')

    # create a new user_profile from RegisteredUser 
    # the key_name is self.user.email(), 
    # main_email is self.user.email()
    # name is person_name
    # interest is topics
    # notification_email is notification_email
    user_profile = RegisteredUser(key_name=_________________,
        main_email=_________________,
        name=___________,
        interests=______,
        notification_email=__________________)
    
    # use the put() method on user_profile to write the entity to the
    # data store
    ____________._____
    """
    self.redirect('/userprofile')


class VenuesPage(webapp2.RequestHandler):
  def get(self):
    template = jinja_environment.get_template('venues.template')
    self.response.out.write(template.render())


class HomePage(webapp2.RequestHandler):
  def get(self):
    template = jinja_environment.get_template('home.template')
    self.response.out.write(template.render())


app = webapp2.WSGIApplication([
  ('/developer', DeveloperPage),
  ('/userprofile', UserProfilePage),
  ('/scheduleconference', ScheduleConferencePage),
  ('/listconferences', ListConferencesPage),
  ('/venues', VenuesPage),
  ('/', HomePage)],
  debug=True)
