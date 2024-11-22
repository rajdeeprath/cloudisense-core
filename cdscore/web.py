'''
 * Copyright (C) 2019-2025 Rajdeep Rath (Cloudisense-core - cdscore)
 * This library (.py files) is intended for use solely within the Cloudisense program and its supporting codebases.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.   
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