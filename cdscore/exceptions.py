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

class TargetServiceError(Exception):
    """Base class for other exceptions"""
    pass


class FileSystemOperationError(Exception):
    """Base class for other exceptions"""
    pass

class FileUploadError(Exception):
    """Base class for other exceptions"""
    pass


class AccessPermissionsError(Exception):
    """Base class for other exceptions"""
    pass


class ConfigurationLoadError(Exception):
    """Base class for other exceptions"""
    pass

class RPCError(Exception):
    """Base class for other exceptions"""
    pass


class ModuleNotFoundError(Exception):
    """Base class for other exceptions"""
    pass


class RunnableScriptError(Exception):
    """Base class for other exceptions"""
    pass

class RulesError(Exception):
    """Base class for other exceptions"""
    pass

class ActionError(Exception):
    """Base class for other exceptions"""
    pass