"""Module for parser class"""
from requests import Response
from bs4 import BeautifulSoup

from .base import BaseClass
from .dataclasses import Faculty, Group, Schedule
from .sender import Sender


class Parser(BaseClass):
    """Parser class to get information from Rozklad ONTU"""
    sender: Sender = None

    def __init__(self, *args, **kwargs):
        if isinstance(kwargs, dict) and 'kwargs' in kwargs:
            # Trick to unwrap kwargs
            kwargs = kwargs.get('kwargs', {})

        self.sender = Sender(*args, **kwargs)

    def _get_page(self, response: Response):
        content = response.content
        if not content:
            raise ValueError(
                f'Response: {response} has no content!',
                response
            )
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

    def get_schedule(self, group_id, all_time=False):
        """
            Returns a schedule for a group (by id)
            If all_time is False - returns schedule for current week
            Else - returns schedule for whole semester
        """
        request_data = {
            'groupid': group_id
        }
        if all_time:
            request_data['show_all'] = 1
        schedule_response = self.sender.send_request(
            method='POST',
            data=request_data
        )
        schedule_page = self._get_page(
            schedule_response
        )

        breadcrumbs = schedule_page.find(
            attrs={
                'class': 'breadcrumbs'
            }
        )
        group_breadcrumbs = breadcrumbs.find_all(
            attrs={
                'class': 'page-link'
            }
        )

        table = schedule_page.find(
            attrs={
                'class': 'table'
            }
        )
        group_name = group_breadcrumbs[-1].text
        # I hate this, but at the same time - I love it
        # If it ever to become broken I'll implement this a bit thoughtfully :)
        subgroup_name = group_name.split('[')[1].replace(']', '')
        schedule = Schedule.from_tag(
            table,
            subgroup=subgroup_name
        )
        week = schedule.week
        return week

    def parse(self, all_time=False):
        """Parses information, requiring user input (CLI)"""
        schedule = None
        all_faculties = self.get_faculties()

        for faculty in all_faculties:
            print(faculty.get_faculty_name())

        faculty_name = input('Введите название факультета: ')
        faculty_id = None
        for faculty in all_faculties:
            if faculty.get_faculty_name() == faculty_name:
                faculty_id = faculty.get_faculty_id()
                break
        else:
            print("Несуществующее имя факльтета!")
            return schedule
        groups = self.get_groups(faculty_id)
        for group in groups:
            print(group.get_group_name())

        group_name = input('Введите название группы: ')
        group_id = None
        for group in groups:
            if group.get_group_name() == group_name:
                group_id = group.get_group_id()
                break
        else:
            print("Несуществующее имя группы!")
            return schedule

        schedule = self.get_schedule(group_id, all_time=all_time)
        return schedule
