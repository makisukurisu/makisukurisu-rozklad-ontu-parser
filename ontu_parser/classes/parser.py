from .base import BaseClass
from .sender import Sender

from bs4 import BeautifulSoup

class Parser(BaseClass):
    sender: Sender = Sender()

    def parse(self):
        base_response = self.sender.send_request('GET')
        faculty_page = BeautifulSoup(base_response.content.decode('utf-8'), 'html.parser')
        all_fcs = faculty_page.find_all(attrs={'class': 'fc'})
        all_fcs_dict = {}
        for fc in all_fcs:
            all_fcs_dict[fc.span.string] = fc['data-id']

        for key in all_fcs_dict.keys():
            print(key)

        faculty_name = input('Введите название факультета: ')
        while True:
            if faculty_name in all_fcs_dict:
                break
            else:
                faculty_name = input('Факультет не найден, попробуйте ещё раз: ')
        groups = self.sender.send_request('POST', {'facultyid': all_fcs_dict[faculty_name]})
        print(groups)