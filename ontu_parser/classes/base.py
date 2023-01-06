"""Module with base classes"""
from attrs import define


@define
class BaseClass:
    """Provides common base for desc"""
    def get_as_str(self):
        """Returns __dict__ in a string format"""
        return str(self.__dict__)

    def get_class_as_str(self):
        """Returns __class__ in a string formt"""
        return str(self.__class__)
