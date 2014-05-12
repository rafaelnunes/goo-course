# -*- coding: utf-8 -*-
'''
Created on Sept 26, 2013

@author: Rafael Nunes
'''
import datetime

from core.base import BaseHandler



class IndexPage(BaseHandler):
    def get(self):
        current_time = datetime.datetime.now()

        return self.render('index.html', current_time=current_time)

    def about(self):
    	return self.render('about.html')

