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