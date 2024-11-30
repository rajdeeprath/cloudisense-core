# Copyright © 2024 Rajdeep Rath. All Rights Reserved.
#
# This codebase is open-source and provided for use exclusively with the Cloudisense platform,
# as governed by its End-User License Agreement (EULA). Unauthorized use, reproduction,
# or distribution of this code outside of the Cloudisense ecosystem is strictly prohibited.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# A copy of the License is available at:
# http://www.apache.org/licenses/LICENSE-2.0
#
# This code may include third-party open-source libraries subject to their respective licenses.
# Such licenses are referenced in the source files or accompanying documentation.
#
# For questions or permissions beyond the scope of this notice, please contact Rajdeep Rath.



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