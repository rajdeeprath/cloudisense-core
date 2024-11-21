'''
This file is part of `Cloudisense` 
Copyright 2018 Connessione Technologies

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import tornado.web
import logging
import tornado.websocket



# Create a base class for logging
class LoggingHandler:
    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger(self.__class__.__name__)




# base class
class BaseRequestHandler(tornado.web.RequestHandler, LoggingHandler):


    def options(self, *args):
        # no body
        # `*args` is for route with `path arguments` supports
        self.set_status(204)
        self.finish()
        

    def set_default_headers(self, *args, **kwargs):
        configuration = self.application.configuration
        server_config = configuration["server"]
        if "cors" in server_config:
            
            cors_config = configuration["server"]["cors"]
            
            if "allow-origin" in cors_config:
                self.set_header("Access-Control-Allow-Origin", cors_config["allow-origin"])
            
            if "allow_headers" in cors_config:
                self.set_header("Access-Control-Allow-Headers", cors_config["allow_headers"])
            
            if "expose_headers" in cors_config:
                self.set_header("Access-Control-Expose-Headers", cors_config["expose_headers"])
                
            if "request_headers" in cors_config:
                self.set_header("Access-Control-Request-Headers", cors_config["request_headers"]) 

            if "allow_methods" in cors_config:
                self.set_header("Access-Control-Allow-Methods", cors_config["allow_methods"])            

            if "allow_credentials" in cors_config:
                self.set_header("Access-Control-Allow-Credentials", cors_config["allow_credentials"])