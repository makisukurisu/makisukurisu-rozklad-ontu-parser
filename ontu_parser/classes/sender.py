import requests

from .base import BaseClass

class RequestsEnum:
    class Methods:
        GET = 'GET'
        POST = 'POST'

        CHOICES = [
            GET, POST
        ]
    class Codes:
        OK = 200


class Sender(BaseClass):
    link: str = 'https://rozklad.ontu.edu.ua/guest_n.php'
    nobot: str = 'ab709742d0971929fd95a7e0d618bc4c'  # temporary
    cookies: dict[str, str] = {}

    _responses: list[requests.Response] = []

    def send_request(self, method:str, data: (dict | None) = None):
        session = requests.Session()
        if method not in RequestsEnum.Methods.CHOICES:
            raise ValueError(
                'arg. `method` should be one of: {}'.format(
                    RequestsEnum.CHOICES
                ),
                method,

            )

        try:
            response = session.request(
                method=method,
                url=self.link,
                cookies=self.cookies,
                data=data
            )
        except Exception as E:
            raise Exception(
                'could not get response from {}, got exception: {}'.format(
                    self.link,
                    E
                )
            )
        if response.status_code != RequestsEnum.Codes.OK:
            raise Exception(
                'server returned non OK response',
                response.status_code,
                response,
                response.content
            )
        #Keep resonses for a little while
        self._responses.append(response)
        self._responses = self._responses[-5:]

        return response
