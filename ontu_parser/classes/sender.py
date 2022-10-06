from datetime import datetime
import requests
from selenium import webdriver

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


class TTLValue(BaseClass):
    _ttl: int = 3600
    _value: object = None

    issued_at: datetime = datetime.min

    def is_valid(self):
        if (datetime.now() - self.issued_at).seconds > self._ttl:
            return True
        else:
            return False

    def set_value(self, value):
        self.issued_at = datetime.now()
        self._value = value


class Cookies(TTLValue):

    def __init__(self, sender):
        self.sender: Sender = sender

    @property
    def value(self)->dict[str, str]:
        if self._value and self.is_valid():
            return self._value
        else:
            self.get_cookie()
            if not self._value:
                raise Exception("Could not get cookies")
            return self._value
    
    def get_cookie(self):
        link = self.sender.link
        notbot = self.sender.notbot.value

        response = requests.get(link, cookies={'notbot': notbot})
        key = 'PHPSESSID'
        cookie = response.cookies.get(key)

        self._value = {key: cookie, 'notbot': notbot}


class NotBot(TTLValue):

    @property
    def value(self)->str:
        if self._value and self.is_valid():
            return self._value
        else:
            self.get_nobot()
            if not self._value:
                raise Exception("Could not get notbot")
            return self._value

    def get_nobot(self):
        driver = webdriver.Firefox()
        driver.get('https://rozklad.ontu.edu.ua/guest_n.php')
        notbot = None
        while True:
            if notbot:
                break
            cookies = driver.get_cookies()
            if cookies:
                for cookie in cookies:
                    if cookie['name'] == 'notbot':
                        notbot = cookie['value']
        self.set_value(notbot)


class Sender(BaseClass):
    link: str = 'https://rozklad.ontu.edu.ua/guest_n.php'
    notbot: NotBot = NotBot()
    cookies: Cookies = None

    def __init__(self):
        self.cookies = Cookies(self)

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
                cookies=self.cookies.value,
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
