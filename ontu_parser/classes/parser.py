"""Module for parser class"""
from requests import Response
from bs4 import BeautifulSoup

from .base import BaseClass
from .dataclasses import Faculty, Group
from .sender import Sender


class Parser(BaseClass):
    """Parser class to get information from Rozklad ONTU"""
    sender: Sender = Sender()

    def _get_page(self, response: Response):
        content = response.content
        if not content:
            raise Exception(f'Response: {response} has no content!')
        decoded_content = content.decode('utf-8')
        return BeautifulSoup(decoded_content, 'html.parser')

    def get_faculties(self) -> list[Faculty]:
        """Returns a list of faculties as Faculty objects"""
        faculties_response = self.sender.send_request(
            method='GET'  # No data gives 'main' page with faculties
        )
        faculty_page = self._get_page(faculties_response)
        faculty_tags = faculty_page.find_all(
            attrs={
                'class': 'fc'  # Faculties have class 'fc'
            }
        )
        faculty_entities = []
        for tag in faculty_tags:
            faculty_entities.append(
                Faculty.from_tag(
                    tag
                )
            )
        return faculty_entities

    def get_groups(self, faculty_id) -> list[Group]:
        """Returns Group list of a faculty by faculty id"""
        groups_response = self.sender.send_request(
            method='POST',
            data={
                'facultyid': faculty_id
            }
        )
        groups_page = self._get_page(groups_response)
        groups_tags = groups_page.find_all(
            attrs={
                'class': 'grp'
            }
        )
        group_entities: list[Group] = []
        for tag in groups_tags:
            group_entities.append(
                Group.from_tag(
                    tag
                )
            )
        return group_entities

    def parse(self):
        """Parses information, requiring user input (CLI)"""
        all_faculties = self.get_faculties()

        for faculty in all_faculties:
            print(faculty.get_name())

        faculty_name = input('Введите название факультета: ')
        faculty_id = None
        for faculty in all_faculties:
            if faculty.get_name() == faculty_name:
                faculty_id = faculty.get_id()
                break
        else:
            print("Несуществующее имя факльтета!")
            return
        groups = self.get_groups(faculty_id)
        for group in groups:
            print(group.get_group_name())
        # TO BE CONTINUED...
