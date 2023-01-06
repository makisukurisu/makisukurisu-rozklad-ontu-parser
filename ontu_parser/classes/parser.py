"""Module for parser class"""
from bs4 import BeautifulSoup

from .base import BaseClass
from .sender import Sender


class Parser(BaseClass):
    """Parser class to get information from Rozklad ONTU"""
    sender: Sender = Sender()

    def parse(self):
        """Parses information, requiring input from user (will be changed)"""
        base_response = self.sender.send_request('GET')
        faculty_page = BeautifulSoup(base_response.content.decode('utf-8'), 'html.parser')
        all_faculties = faculty_page.find_all(attrs={'class': 'fc'})
        all_faculties_dict = {}
        for faculty in all_faculties:
            all_faculties_dict[faculty.span.string] = faculty['data-id']

        for key in all_faculties_dict:
            print(key)

        faculty_name = input('Введите название факультета: ')
        while True:
            if faculty_name in all_faculties_dict:
                break
            faculty_name = input('Факультет не найден, попробуйте ещё раз: ')
        groups = self.sender.send_request('POST', {'facultyid': all_faculties_dict[faculty_name]})
        print(groups)
