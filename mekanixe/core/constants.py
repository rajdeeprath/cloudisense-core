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


''' attribute names'''

ATTR_CHUNK_COLLECTOR = "chunk_collector"

ATTR_CONTENT = "content"

ATTR_NAME = "name"

ATTR_LOG_NAME = "log_name"


''' event action constants'''

EVENT_STATE_START = "start"

EVENT_STATE_STOP = "stop"

EVENT_STATE_PROGRESS = "progress"



''' topic names'''

TOPIC_ANY = "*"

TOPIC_LOG_ACTIONS = "/logging/actions"

TOPIC_LOGMONITORING = "/logging"

TOPIC_STATS = "/stats"

TOPIC_SYSTEM_PROCESS = "/system/process"

TOPIC_PING = "/ping"

TOPIC_UI_INITIALIZATION = "/ui/guide"

TOPIC_NOTIFICATION = "/notification"

TOPIC_SCRIPTS = "/script"

TOPIC_DELEGATE_MONITORING = "/targetdelegate"

TOPIC_NOTIFICATIONS = "/notifications"

TOPIC_IDENTITY = "/internal/identity"

TOPIC_UI_UPDATES = "/ui/updates"


''' Notification codes'''

NOTIFICATIONS_NOTICE = 0

NOTIFICATIONS_ERROR = 1

NOTIFICATIONS_WARN = 2



''' Moduile names'''

SYSTEM_MODULE = "sysmon"

FILE_MANAGER_MODULE = "file_manager"

UI_MODELER_MODULE = "ui_modeler"

PUBSUBHUB_MODULE = "pubsub"

LOG_MANAGER_MODULE = "log_monitor"

PINGER_MODULE = "pinger"

TARGET_DELEGATE_MODULE = "target_delegate"

RPC_GATEWAY_MODULE = "rpc_gateway"

MQTT_GATEWAY_MODULE = "mqtt_gateway"

SMTP_MAILER_MODULE = "smtp_mailer"

SCRIPT_RUNNER_MODULE = "script_runner"

SCHEDULER_MODULE = "scheduler"

BOT_SERVICE_MODULE = "service_bot"

REACTION_ENGINE_MODULE = "reaction_engine"

SECURITY_PROVIDER_MODULE = "security_provider"



''' client channel names'''

CHANNEL_HTTP_REST = "http_rest_channel"

CHANNEL_WEBSOCKET_RPC = "websocket_rpc_channel"

CHANNEL_SMTP_MAILER = "smtp_mailer_channel"

CHANNEL_RTMP = "rtmp_channel"

CHANNEL_CHAT_BOT = "chat_bot_channel"

CHANNEL_MQTT = "mqtt_channel"



''' client type'''

PROACTIVE_CLIENT_TYPE = "proactive_client_type"

REACTIVE_CLIENT_TYPE = "reactive_client_type"

def built_in_client_types():
    return [PROACTIVE_CLIENT_TYPE, REACTIVE_CLIENT_TYPE]



''' role type'''

ADMIN_ROLE = "admin"

DEVELOPER_ROLE = "developer"

OBSERVER_ROLE = "observer"

def built_in_user_roles():
    return [ADMIN_ROLE, DEVELOPER_ROLE, OBSERVER_ROLE]

''' function names '''

GET_UI_ACTIONS = "get_ui_actions"

''' OS TYPE '''
OS_TYPE_LINUX = "Linux"
OS_TYPE_WINDOWS = "Windows"
OS_TYPE_MAC = "Mac"