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
    def _check_tag(tag):
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

    def get_picture(self):
        """Returns relative link to picture (if present)"""
        return self.faculty_tag.attrs.get('data-cover', None)

    def get_id(self):
        """Returns temporary id of faculty (for later use in search)"""
        return self.faculty_tag.attrs['data-id']

    def get_name(self):
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
