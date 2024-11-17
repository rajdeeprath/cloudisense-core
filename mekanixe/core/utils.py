from mekanixe.handlers import base
from tornado.web import url
from typing import List



def get_url_patterns(rest:bool, ws:bool)->List:
    
    if rest and not ws:
        return [
            url(r"/", base.MainHandler)
            ]
    elif ws and not rest:
        return [
            url(r"/ws", base.WebSocketHandler),
            ]
    elif ws and rest:
        return [
            url(r"/", base.MainHandler),
            url(r"/ws", base.WebSocketHandler)
            ]