"""Enumerators"""
from enum import Enum


class RequestsEnum:
    """Contains information for Requests library"""

    class Methods(Enum):
        """Contains used HTTP Methods for requests"""

        GET = "GET"
        POST = "POST"

        CHOICES = [GET, POST]

    class Codes(Enum):
        """Contains used HTTP response codes"""

        OK = 200

    @classmethod
    def code_ok(cls):
        """
        OK code

        Returns:
            int: 200, Codes.OK
        """
        return cls.Codes.OK.value

    @classmethod
    def method_get(cls):
        """Method GET

        Returns:
            str: GET
        """
        return cls.Methods.GET.value

    @classmethod
    def method_post(cls):
        """Method POST

        Returns:
            str: POST
        """
        return cls.Methods.POST.value
