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