class DomainException(Exception):
    pass

class NegativeVolumeException(DomainException):
    pass

class DispatchNotFoundException(DomainException):
    pass
