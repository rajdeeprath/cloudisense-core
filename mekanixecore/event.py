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

import datetime

from builtins import int
from typing import Dict, Text, Any, Optional

from mekanixecore.constants import TOPIC_NOTIFICATION, TOPIC_UI_INITIALIZATION, TOPIC_UI_UPDATES



'''

EVENT CONSTANTS

'''


EVENT_ANY = "*"

EVENT_PING_GENERATED = "ping_generated"

EVENT_TEXT_NOTIFICATION = "text_notification"

EVENT_UI_UPDATE = "ui_update"

EVENT_TEXT_DATA_NOTIFICATION = "text_data_notification"

EVENT_ARBITRARY_DATA = "data_generated"

EVENT_ARBITRARY_ERROR = "error_generated"

EVENT_LOG_RECORDING_START = "log_record_start"

EVENT_LOG_RECORDING_STOP = "log_record_stop"

EVENT_KEY = "__event__"


'''

EVENTS

'''


EventType = Dict[Text, Any]




def is_valid_event(evt)->bool:
    
    if "name" in evt and "type" in evt and "topic" in evt:
        return True
    
    return False


def utc_timestamp():
    return int(datetime.datetime.utcnow().timestamp() * 1000)



# noinspection PyPep8Naming
def UIEvent(
    message: Text,
    data: Optional[Dict[Text, Any]] = None,
    meta: Optional[Dict[Text, Any]] = None,
    timestamp: Optional[float] = None,
) -> EventType:
    return {
        "name": EVENT_UI_UPDATE,
        "type": "event",
        "status": "data",
        "topic": TOPIC_UI_INITIALIZATION,
        "data": {"message": message, "data": data},
        "meta": meta,
        "timestamp": utc_timestamp() if timestamp == None else timestamp
    }





# noinspection PyPep8Naming
def UIUpdateEvent(
    datakey: Text,
    data: Dict[Text, Any] = None,  
    meta: Optional[Dict[Text, Any]] = None,
    timestamp: Optional[float] = None,
) -> EventType:
    return {
        "name": EVENT_UI_UPDATE,
        "type": "event",
        "status": "data",
        "topic": TOPIC_UI_UPDATES,
        "data": {"datakey": datakey, "data": data},
        "meta": meta,
        "timestamp": utc_timestamp() if timestamp == None else timestamp
    }




# noinspection PyPep8Naming
def SimpleNotificationEvent(
    message: Text,
    code: int,
    data: Optional[Dict[Text, Any]] = None,
    meta: Optional[Dict[Text, Any]] = None,
    timestamp: Optional[float] = None,
) -> EventType:
    '''
    Code denotes intent. It can be from 1 to 4.
    Intent is used to match coloring of notification on client side
    
    1 -> INFO
    2 -> SUCCESS
    3 -> WARN
    4 -> ERROR
    '''
    return {
        "name": EVENT_TEXT_NOTIFICATION,
        "type": "event",
        "status": "data",
        "topic": TOPIC_NOTIFICATION,
        "data": {"message": message, "code": code, "data": data},
        "meta": meta,
        "timestamp": utc_timestamp() if timestamp == None else timestamp
    }
    


# noinspection PyPep8Naming
def DataEvent(
    topic: Text,
    data: Optional[Dict[Text, Any]] = None,
    meta: Optional[Dict[Text, Any]] = None,
    timestamp: Optional[float] = None,
) -> EventType:
    return {
        "name": EVENT_ARBITRARY_DATA,
        "type": "event",
        "status": "data",
        "topic": topic,
        "data": data,
        "meta": meta,
        "timestamp": utc_timestamp() if timestamp == None else timestamp
    }




# noinspection PyPep8Naming
def ErrorEvent(
    topic: Text,
    message: Text = None,
    data: Optional[Dict[Text, Any]] = None,
    meta: Optional[Dict[Text, Any]] = None,
    timestamp: Optional[float] = None,
) -> EventType:
    return {
        "name": EVENT_ARBITRARY_ERROR,
        "status": "error",
        "topic": topic,
        "data": {"message":message, "data": data},
        "meta": meta,
        "timestamp": utc_timestamp() if timestamp == None else timestamp
    }





# noinspection PyPep8Naming
def SystemDataEvent(
    topic: Text,
    data: Optional[Dict[Text, Any]] = None,
    meta: Optional[Dict[Text, Any]] = None,
    timestamp: Optional[float] = None,
) -> EventType:
    return DataEvent(
        topic=topic,
        data=data,
        meta=meta,
        timestamp=timestamp
    )
    
    

# noinspection PyPep8Naming
def SystemErrorEvent(
    topic: Text,
    error: Text,
    meta: Optional[Dict[Text, Any]] = None,
    timestamp: Optional[float] = None,
) -> EventType:
    return ErrorEvent(
        topic=topic,
        message=error,
        data={"message": str(error, 'utf-8')},
        meta=meta,
        timestamp=timestamp
        )



# noinspection PyPep8Naming
def LogErrorEvent(
    topic: Text,
    logkey: Text,
    error: Text,
    meta: Optional[Dict[Text, Any]] = None,
    timestamp: Optional[float] = None,
) -> EventType:  
    return ErrorEvent(
        topic=topic,
        message=error,
        data={"name":logkey},
        meta=meta,
        timestamp=timestamp
        ) 
    
    

# noinspection PyPep8Naming
def LogEvent(
    topic: Text,    
    logkey: Text,
    logdata: Text,
    meta: Optional[Dict[Text, Any]] = None,
    timestamp: Optional[float] = None,
) -> EventType:
    return DataEvent(
        topic=topic,
        data={"name":logkey, "data": str(logdata, 'utf-8')},
        meta=meta,
        timestamp=timestamp
    )
    
    

# noinspection PyPep8Naming
def LogChunkEvent(
    topic: Text,
    logkey: Text,
    chunk: Text,    
    meta: Optional[Dict[Text, Any]] = None,
    timestamp: Optional[float] = None,
) -> EventType:
    '''
        Internal event. Not for client consumption
    '''
    return DataEvent(
        topic=topic,
        data={"name":logkey, "chunk": chunk},
        meta=meta,
        timestamp=timestamp
    )


# noinspection PyPep8Naming
def ScriptExecutionEvent(
    topic: Text,
    script: Text,    
    state:Text,
    output: Text=None,    
    meta: Optional[Dict[Text, Any]] = None,
    timestamp: Optional[float] = None,
) -> EventType:
    '''
        Internal event. Not for client consumption
    '''
    return DataEvent(
        topic=topic,
        data={"script": script, "state": state, "data": str(output)},
        meta=meta,
        timestamp=timestamp
    )
    
    


# noinspection PyPep8Naming
def StartLogRecordingEvent(
    topic: Text,
    data: Optional[Dict[Text, Any]] = None,
    meta: Optional[Dict[Text, Any]] = None,
    timestamp: Optional[float] = None,
) -> EventType:
    '''
        Internal event. Not for client consumption
    '''
    return {
        "name": EVENT_LOG_RECORDING_START,
        "status": "data",
        "type": "event",
        "topic": topic,
        "data": data,
        "meta": meta,
        "timestamp": utc_timestamp() if timestamp == None else timestamp
    }





# noinspection PyPep8Naming
def StopLogRecordingEvent(
    topic: Text,
    data: Optional[Dict[Text, Any]] = None,
    meta: Optional[Dict[Text, Any]] = None,
    timestamp: Optional[float] = None,
) -> EventType:
    return {
        "name": EVENT_LOG_RECORDING_STOP,
        "status": "data",
        "type": "event",
        "topic": topic,
        "data": data,
        "meta": meta,
        "timestamp": utc_timestamp() if timestamp == None else timestamp
    }



# noinspection PyPep8Naming
def PingEvent(
    topic: Text,
    data: Optional[Dict[Text, Any]] = None,
    meta: Optional[Dict[Text, Any]] = None,
    timestamp: Optional[float] = None,
) -> EventType:
    return {
        "name": EVENT_PING_GENERATED,
        "type": "event",
        "status": "data",
        "topic": topic,
        "data": data,
        "meta": meta,
        "timestamp": utc_timestamp() if timestamp == None else timestamp
    }  




