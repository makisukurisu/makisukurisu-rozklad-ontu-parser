"""
    Contains classes needed to get data
    Like Faculty or Group, provides methods to get names, ids, etc.
"""
from attrs import define

from bs4.element import Tag

from .base import BaseClass


class CheckTag:
    """Mixin for _check_tag method"""
    @staticmethod
    def _check_tag(tag: Tag):
        """Checks if tag is valid for usage"""
        raise Exception("`_check_tag` Not implemented")


class BaseTagClass(BaseClass, CheckTag):
    """Base Tag Class for parsing BS4 tags from responses"""
    @classmethod
    def from_tag(cls, tag):
        """Checks tag and returns initialized object"""
        raise Exception("`from_tag` Not implemented")


@define
class Faculty(BaseTagClass):
    """Describes faculty from BS4 tag"""
    faculty_tag: Tag

    @staticmethod
    def _check_tag(tag):
        attrs = getattr(tag, 'attrs', None)
        span = getattr(tag, 'span', None)
        required_properties = [attrs, span]
        if not all(required_properties):
            raise Exception(f"Invalid tag: {tag}, has no attrs")
        required = ['data-id']
        for requirement in required:
            if requirement not in attrs:
                raise Exception(f"Invalid tag: {tag}, doesn't have attrs: {required}")
        span_string = getattr(span, 'string', None)
        if span_string is None:
            raise Exception(f"Invalid tag: {tag}, `span` has no string")

    @classmethod
    def from_tag(cls, tag):
        cls._check_tag(tag)
        return cls(faculty_tag=tag)

    def get_faculty_picture(self):
        """Returns relative link to picture (if present)"""
        return self.faculty_tag.attrs.get('data-cover', None)

    def get_faculty_id(self):
        """Returns temporary id of faculty (for later use in search)"""
        return self.faculty_tag.attrs['data-id']

    def get_faculty_name(self):
        """Returns name of the faculty"""
        return self.faculty_tag.span.string


@define
class Group(BaseTagClass):
    """Describes group from BS4 tag"""

    group_tag: Tag

    _icon_tag_filter = {'attrs': {'class': 'icon'}}
    _text_tag_filter = {'attrs': {'class': 'branding-bar'}}

    @staticmethod
    def _check_tag(tag):
        attrs = getattr(tag, 'attrs', None)
        required = ['data-id']
        for requirement in required:
            if requirement not in attrs:
                raise Exception(f"Invalid tag: {tag}, doesn't have attrs: {required}")

        # Children requiremenets

        icon = tag.find(
            **Group._icon_tag_filter
        )
        text = tag.find(
            **Group._text_tag_filter
        )
        required = [icon, text]
        if not all(required):
            raise Exception(f"Invalid tag: {tag} doesn't have suitable children")

    @classmethod
    def from_tag(cls, tag):
        cls._check_tag(tag)
        return cls(group_tag=tag)

    @property
    def text(self):
        """Returns text tag from group tag"""
        return self.group_tag.find(
            **self._text_tag_filter
        )

    @property
    def icon(self):
        """Returns icon tag from group tag"""
        return self.group_tag.find(
            **self._icon_tag_filter
        )

    def get_group_id(self):
        """Returns (temporary) id of this group"""
        return self.group_tag.attrs['data-id']

    def get_group_name(self):
        """Retunrs a name of the group or None"""
        if not self.text:
            print(f"text tag not found in {self.group_tag}")
            return None
        return self.text.string

    def get_group_icon(self):
        """Returns name of the icon of the group or None"""
        if not self.icon:
            print(f"icon tag not found in {self.group_tag}")
            return None
        # Hardcoding this
        attrs = self.icon.attrs.copy()
        # Feels bad :(
        attrs.pop('icon')
        return attrs[0]


class Schedule(BaseTagClass):
    """Describes schedule from HTML table"""

    schedule_table: Tag
    subgroups: list[str] = []
    _schedule_data: dict = {}

    _splitter_class = 'bg-darkCyan'

    _all_time = False

    @property
    def week(self):
        """Gets data for this week"""
        if not self._schedule_data:
            self._get_week()
        return self._schedule_data

    @staticmethod
    def _check_tag(tag):
        if tag.name != 'table':
            raise Exception(f"Invalid tag: {tag}. Should be table")

    @classmethod
    def from_tag(cls, tag, is_all_time=False):
        cls._check_tag(tag)
        obj = cls()
        obj.schedule_table = tag
        obj._all_time = is_all_time
        return obj

    def _parse_subgroups(self):
        """This method prepares subgroups for later use"""
        sub_groups_list = []
        table_head = self.schedule_table.thead
        head_rows = table_head.find_all(
            name='tr'
        )

        # Hardcoding positions! Yikes!
        # head_rows[0] - meta info (`Day`, `Pair` columns, Group name)
        # head_rows[1] - sub_groups (a/b etc)

        sub_groups_tag = head_rows[1]
        sub_groups_tags = sub_groups_tag.find_all(
            name='th'
        )

        for sub_group in sub_groups_tags:
            sub_groups_list.append(sub_group.text.strip())

        self.subgroups = sub_groups_list

    def _prepare_day_tag(self, day_name_tag):
        """
            Parses day from 'day_name_tag'*
            Returns name of that day and a list of tags that represent pairs

            *day_name_tag is a tag that contains name of the tag
             It also has attr - class = day
        """
        pair_tags = []

        day_name: str = day_name_tag.text

        first_pair_tag = day_name_tag.parent
        # We also have to include this 'top tag', since it's first pair
        pair_tags.append(first_pair_tag)

        next_pair_tag = first_pair_tag.next_sibling
        # next_sibling gives next tag on the same level of hierarchy
        while True:
            if not next_pair_tag or isinstance(next_pair_tag, str):
                # We may not have next sibling
                # Or, as it happens RN - we may get '  ' as next tag :|
                break
            if self._splitter_class in next_pair_tag.attrs.get('class', []):
                # splitter has class `_splitter_class` (like bg-darkCyan)
                # if we hit splitter - day has ended
                break
            pair_tags.append(next_pair_tag)
            next_pair_tag = next_pair_tag.next_sibling
        pair_tags.pop()
        return day_name, pair_tags

    def _prepare_tags(self, tags):
        if self._all_time:
            # Find out, if it's worth the hustle
            if tags:
                return True
            return False
        return False

    def _get_week(self):
        """Iteratively loops trough table to get data for all days"""
        table_body = self.schedule_table.tbody
        days = table_body.find_all(
            attrs={
                'class': 'day'
            }
        )
        for day in days:
            day_name, tags = self._prepare_day_tag(day)
            prepared_days = self._prepare_tags(tags)
            self._schedule_data[day_name] = prepared_days
        return self._schedule_data
