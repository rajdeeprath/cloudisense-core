'''
This file is part of `cloudmechanik` 
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
from typing import Any, Dict

import distro
from mekanixe.core.constants import OS_TYPE_LINUX, OS_TYPE_MAC, OS_TYPE_WINDOWS
from mekanixe.core.intent import INTENT_WRITE_LOG_CHUNKS_NAME
from mekanixe.core.event import DataEvent, SimpleNotificationEvent
from tornado import httputil
from urllib import parse
from jsonschema import validate
from datetime import datetime
from collections import deque
from sys import platform

import ntpath
import os
import json
import filetype
import base64



def build_script_topic_path(seed:str, *params:str):
    path:str = ""
    for param in params:
        path = path + "/" + param

    return path



def has_uuid_message(msg):
    if "session-id" in msg:
        if msg["session-id"] != None and msg["session-id"] != "":
            return True
        
    return False



def has_sender_id_message(msg):
    if "client-id" in msg:
        if msg["client-id"] != None and msg["client-id"] != "":
            return True
        
    return False



def is_command_message(data:Dict):

    schema = {
        "type" : "object",
        "properties" : {
            "client-id" : {"type" : "string"},
            "session-id" : {"type" : "string"},
            "intent" : {"type" : "string"},
            "timestamp" : {"type" : "number"},
            "data" : {
                "type" : "object",
                "properties" : {
                    "params" : {"type" : "object"},
                    "res-topic" : {"type" : "string"}
                },
                "required": ["params"]
            }
        },
        "required": ["client-id", "session-id", "intent", "timestamp", "data"]
    }

    
    try:
        validate(instance=data, schema=schema)
        return True
    except:
        return False
    pass



def is_data_message(data:Dict):

    schema = {
        "type" : "object",
        "properties" : {
            "client-id" : {"type" : "string"},
            "session-id" : {"type" : "string"},
            "intent" : {"type" : "string"},
            "timestamp" : {"type" : "number"},
            "data" : {
                "type" : "object",
                "properties" : {
                    "params" : {"type" : "object"},
                    "res-topic" : {"type" : "string"}
                },
                "required": ["params"]
            }
        },
        "required": ["client-id", "session-id", "intent", "timestamp", "data"]
    }
    
    
    try:
        validate(instance=data, schema=schema)
        return True
    except:
        return False
    pass





def requires_ack_message(msg):
    
    if "data" in msg:
        if msg["data"] != None and msg["data"] != "":
            if "res-topic" in msg["data"]:
                if msg["data"]["res-topic"] != None and msg["data"]["res-topic"] != "":
                    return True
        
    return False



def is_notification_event(evt):
    
    if "type" in evt:
        if evt["type"] == "NotificationEvent":
                return True
    
    return False



def isVideo(obj):
    
    if 'data' in  obj:
        kind = filetype.guess(obj['data'])
        if kind is None:
            return False
        elif 'video' in kind.mime:
            return True
    
    return False


def isImage(obj):
    
    if 'data' in  obj:
        kind = filetype.guess(obj['data'])
        if kind is None:
            return False
        elif 'image' in kind.mime:
            return True
    
    return False


def isJSON(obj):
    try:
        json_object = json.loads(str(obj))
    except ValueError as e:
        return False
    return True


def hasFunction(obj, methodname):
    invert_op = getattr(obj, methodname, None)
    return True if callable(invert_op) else False


def buildTopicPath(topic, subtopic):
    return topic + "/" + subtopic


def getLogFileKey(path):
    return str(path_leaf(path))


def path_leaf(path):
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)
    

''' creates dynamic log writer rule dynamically '''        
def buildLogWriterRule(rule_id, topic, filepath):
    name = path_leaf(filepath)
    output_path = os.path.join(os.path.dirname(filepath),  "ondemand-" + rule_id)
    return{
            "id": rule_id,
            "description": "Rule for log recording " + name,
            "listen-to": ""+ topic + "",
            "enabled": True,
            "trigger":{
                "on-payload-object": {
                    "key":"data",
                    "on-content": "*",
                    "on-condition": "equals"
                },        
                "evaluator": None
            },
            "response":{
                "intent": "" + INTENT_WRITE_LOG_CHUNKS_NAME + "",
                "parameters": {
                    "destination": "" + output_path + ""
                }
            }    
        }
    
    
    pass






def stringToBase64(s):
    return base64.b64encode(s.encode('utf-8'))


def base64ToString(b):
    return base64.b64decode(b).decode('utf-8')



def formatSuccessMQTTResponse(requestid, data={}, code=200):
    return {
            "session-id": str(requestid),
            "type": "mqtt",
            "status": "success",
            "code": code,
            "data": data,
            "timestamp":int(datetime.utcnow().timestamp())
            }



def formatErrorMQTTResponse(requestid, message, code=400):
    return {
            "session-id": str(requestid),
            "type": "mqtt",
            "status": "error",
            "code": code,
            "message": message,
            "timestamp":int(datetime.utcnow().timestamp())
            }



def formatAckMQTTResponse(requestid, code=200):
    return {
            "session-id": str(requestid),
            "type": "mqtt",
            "status": "ack",
            "code": code,
            "timestamp":int(datetime.utcnow().timestamp())
            }



def formatSuccessRPCResponse(requestid, data, code=200):
    return {
            "requestid": str(requestid),
            "type": "rpc",
            "status": "success",
            "code": code,
            "data": data,
            "timestamp":int(datetime.utcnow().timestamp())
            }



def formatErrorRPCResponse(requestid, message, code=400):
    return {
            "requestid": str(requestid),
            "type": "rpc",
            "status": "error",
            "code": code,
            "message": message,
            "timestamp":int(datetime.utcnow().timestamp())
            }
    
def formatSuccessResponse(data, code=200):
    return {
            "status": "success",
            "code": code,
            "data": data,
            "timestamp":int(datetime.utcnow().timestamp())
            }


def getTokensAuthorizationTokens(request: httputil.HTTPServerRequest):
    bearer_data:str = request.headers.get("Authorization", None)
    if bearer_data != None:
        bearer_data = bearer_data.replace("Bearer", "")
        bearer_data = bearer_data.strip(); 
        tokens = dict(parse.parse_qsl(bearer_data))
        return tokens
    else:
        raise LookupError("Authorization data (Bearer) not found in header")
    pass


def formatProgressResponse(permit, data):
    return {
            "permit": permit,
            "code": 200,
            "start_time": data["start_time"],
            "end_time": data["end_time"],
            "total_bytes": data["total_bytes"],
            "uploaded_bytes": data["uploaded_bytes"],
            "timestamp":int(datetime.utcnow().timestamp())
            }


def formatErrorResponse(message, code):
    return {
            "status": "error",
            "code": code,
            "message": message,
            "timestamp":int(datetime.utcnow().timestamp())
            }



def buildSimpleNotificationEvent(topic, msg, code, meta=None):
    return SimpleNotificationEvent(topic=topic,message=msg, code=code, meta=meta)



def buildDataNotificationEvent(msg, code, data, meta=None):    
    return SimpleNotificationEvent(code=code, message=msg, data=data, meta=meta)


def buildDataEvent(data, topic, meta=None):
    return DataEvent(topic=topic, data=data, meta=meta)



def formatSuccessBotResponse(requestid, data):
    return data
    pass


def formatErrorBotResponse(requestid, error):
    return "An error occurred "  + str(error)
    pass


def get_current_utc_time_milliseconds()->int:
    date= datetime.utcnow() - datetime(1970, 1, 1)
    seconds =(date.total_seconds())
    milliseconds = round(seconds*1000)
    return milliseconds

def get_os_information()->Dict:
    os_details = {}
    os_details["type"] = "Unknown"

    if platform == "linux" or platform == "linux2":
        os_details["type"] = OS_TYPE_LINUX        
    elif platform == "darwin":
        os_details["type"] = OS_TYPE_MAC
    elif platform == "win32":
        os_details["type"] = OS_TYPE_WINDOWS
    
    return os_details


def getSystemTime():
    '''
        Returns system time formatted in human readable format
    '''
    now = datetime.now()
    return datetime.strftime(now, '%H:%M:%S')



def build_software_version_info_string(os_type, os_name, os_version, python_version, program_version, timezoneinfo ):
        return {
            "os": os_type + " " + os_name + " " + os_version,
            "programs": "Python : " + python_version + ", " + "CloudMechanik : " + program_version,
            "timezone": timezoneinfo
        }


def getPieChartMappableData(usedpct:int)->list:        
    '''
        Converts a percentage value to pie chart mappable data (targetting chartjs)
    '''
    return [usedpct, (100-usedpct)] # used | free


def getLineChartMappableData(samples:deque, xlabel:str, ylabel:str)->list:
    '''
        Converts a deque of cpu usage samples over time points to line chart mappable data (targetting chartjs)
    '''
    xaxis = []
    yaxis = []
    for item in list(samples):
        yaxis.append(item[0]) # value
        xaxis.append(item[1]) # datetime
    
    return {
        "data": {
                "xaxis":{
                    "label": xlabel,
                    "data": xaxis
                },
                "yaxis":[{
                    "label": ylabel,
                    "data": yaxis
                }]
            }        
        }
