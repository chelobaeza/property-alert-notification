

class ServiceException(Exception):
    pass

class PreferencesNotFound(ServiceException):
    pass

class PreferencesAlreadyExist(ServiceException):
    pass