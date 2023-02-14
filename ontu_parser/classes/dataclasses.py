"""
    Contains classes needed to get data
    Like Faculty or Group, provides methods to get names, ids, etc.
"""
from attrs import define

from bs4.element import Tag

from .base import BaseClass


class CheckTagMixin:
    """Mixin for _check_tag method"""
    @staticmethod
    def _check_tag(tag: Tag):
        """Checks if tag is valid for usage"""
        raise NotImplementedError("`_check_tag` Not implemented")


class BaseTag(BaseClass, CheckTagMixin):
    """Base Tag Class for parsing BS4 tags from responses"""
    @classmethod
    def from_tag(cls, tag):
        """Checks tag and returns initialized object"""
        raise NotImplementedError("`from_tag` Not implemented")


@define
class Faculty(BaseTag):
    """Describes faculty from BS4 tag"""
    faculty_tag: Tag

    @staticmethod
    def _check_tag(tag):
        attrs = getattr(tag, 'attrs', None)
        span = getattr(tag, 'span', None)
        required_properties = [attrs, span]
        if not all(required_properties):
            raise ValueError(f"Invalid tag: {tag}, has no attrs", tag)
        required = ['data-id']
        for requirement in required:
            if requirement not in attrs:
                raise ValueError(
                    f"Invalid tag: {tag}, doesn't have attrs: {required}",
                    tag,
                    required
                )
        span_string = getattr(span, 'string', None)
        if span_string is None:
            raise ValueError(
                f"Invalid tag: {tag}, `span` has no string",
                tag
            )

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
class Group(BaseTag):
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
                raise ValueError(
                    f"Invalid tag: {tag}, doesn't have attrs: {required}",
                    tag,
                    required
                )

        # Children requiremenets

        icon = tag.find(
            **Group._icon_tag_filter
        )
        text = tag.find(
            **Group._text_tag_filter
        )
        required = [icon, text]
        if not all(required):
            raise ValueError(
                f"Invalid tag: {tag} doesn't have suitable children",
                tag
            )

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
        return self.group_tag.attrs["data-id"]

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


class BaseLesson(BaseTag):
    """
        Describes lesson from bs4 tag

        Note: Lesson is a concrete even with date and teacher
        Pair on the other hand just states at which time lesson will happen
    """

    lesson_tag: Tag

    lesson_date: str = ""
    teacher: dict = {}
    lesson_name: dict = {}
    lesson_info: str = ""

    @staticmethod
    def _check_tag(tag: Tag):
        # Dear Gods, forgive me for not checking tags for lessons
        pass

    def parse_tag(self):
        """This method parses bs4 and stores data from it in object's fields"""
        raise NotImplementedError(
            "`parse_tag` was not implemented\n"
            "You are probably executing this from BaseLesson\n"
            "Please use one of derived classes"
        )


class AllTimeLesson(BaseLesson):
    """
        This class should be used to parse lesson from bs4 tag
        If you are getting schedule for all time
    """
    @classmethod
    def from_tag(cls, tag):
        obj = cls()
        obj.lesson_tag = tag
        obj.parse_tag()
        return obj

    def parse_tag(self):
        lesson = self.lesson_tag
        self.lesson_date = lesson.text
        predm = lesson.nextSibling
        self.lesson_name = {
            'short': predm.text,
            'full': predm.attrs.get('title', "Not Set")
        }
        prp = predm.nextSibling
        if isinstance(prp, str):
            # <br> may be interpreted as '\n'
            prp = prp.nextSibling
        self.teacher = {
            'short': prp.text.replace('\xa0', ' '),  # Why...
            'full': prp.attrs.get('title', "Not Set")
        }
        card = prp.nextSibling
        if isinstance(card, str):
            # <br> may be interpreted as '\n'
            card = card.nextSibling
        card_content: Tag = card.find(
            attrs={
                'class': 'card-content'
            }
        )
        if card_content:
            self.lesson_info = card_content.text.replace('\t', '')


class RegularLesson(BaseLesson):
    """
        This class should be used to parse lesson from bs4 tag
        If you are getting schedule for current week
    """
    @classmethod
    def from_tag(cls, tag):
        obj = cls()
        obj.lesson_tag = tag
        obj.parse_tag()
        return obj

    def parse_tag(self):
        lesson = self.lesson_tag
        # I don't know why, but ok :)
        skip = lesson.nextSibling
        self.lesson_name = {
            'short': lesson.text,
            'full': lesson.attrs.get('title', "Not Set")
        }
        prp = skip.nextSibling
        if isinstance(prp, str):
            # <br> may be interpreted as '\n'
            prp = prp.nextSibling
        self.teacher = {
            'short': prp.text.replace('\xa0', ' '),  # Why...
            'full': prp.attrs.get('title', "Not Set")
        }
        card = prp.nextSibling
        if isinstance(card, str):
            # <br> may be interpreted as '\n'
            card = card.nextSibling
        card_content: Tag = card.find(
            attrs={
                'class': 'card-content'
            }
        )
        if card_content:
            self.lesson_info = card_content.text.replace('\t', '')


class Pair(BaseTag):
    """
        Describes pair from bs4 tag

        Note: Pair describes when certain Lesson will happen
    """

    pair_tag: Tag
    lessons: list[BaseLesson] = []

    pair_no: int = None
    _subgroup_id: int = 0

    @staticmethod
    def _check_tag(tag: Tag):
        pass

    @classmethod
    def from_tag(cls, tag, subgroup_id=0):
        cls._check_tag(tag)
        obj = cls()
        obj._subgroup_id = subgroup_id

        obj.pair_tag = tag
        obj.set_pair_number()
        pair = obj.get_pair_tag_for_subgroup()
        lessons = cls.get_lessons(pair)
        obj.lessons = lessons
        return obj

    def set_pair_number(self):
        """This method gets pair number for better identification"""
        pair_no_tag = self.pair_tag.find(
            attrs={
                'class': 'lesson'
            }
        )
        self.pair_no = int(pair_no_tag.text)

    def get_pair_tag_for_subgroup(self):
        """
            This method returns tag for this pair accounting for subgroup
            Currently opening a page for subgroup (like KN-321[a]) opens
            a page for both subgroups (or a group), thus we have to get a correct cell
        """
        pair_no_tag = self.pair_tag.find(
            attrs={
                'class': 'lesson'
            }
        )
        skip = 1 + self._subgroup_id
        pair_tag = None
        for _ in range(skip):
            if not pair_tag:
                pair_tag = pair_no_tag.nextSibling
            else:
                pair_tag = pair_tag.nextSibling
        return pair_tag

    @staticmethod
    def get_lessons(pair: Tag):
        """Parses lessons for this pair"""
        # All dates have this class
        all_dates = pair.find_all(
            attrs={
                'class': 'fg-blue'
            }
        )
        # There is at least one tag with this class if
        # there are lessons
        lesson = pair.find(
            attrs={
                'class': 'predm'
            }
        )
        lessons = []
        if not any([len(all_dates), lesson]):
            return lessons
        if len(all_dates) > 0:
            # This means we are dealing with 'all time' records
            for lesson in all_dates:
                lessons.append(
                    AllTimeLesson.from_tag(
                        lesson
                    )
                )
            return lessons
        # This means we are dealing with single week records
        lessons.append(
            RegularLesson.from_tag(
                lesson
            )
        )
        return lessons


class Schedule(BaseTag):
    """Describes schedule from HTML table"""

    schedule_table: Tag
    subgroups: list[str] = []
    subgroup_id: int = 0
    _schedule_data: dict[str, list[Pair]] = {}
    _subgroup: str = ''

    _splitter_class: str = 'bg-darkCyan'

    @property
    def week(self):
        """Gets data for this week"""
        self._get_week()
        return self._schedule_data

    @staticmethod
    def _check_tag(tag):
        if tag.name != 'table':
            raise ValueError(
                f"Invalid tag: {tag}. Should be table",
                tag
            )

    @classmethod
    def from_tag(cls, tag, subgroup=None):
        cls._check_tag(tag)
        obj = cls()
        obj.schedule_table = tag

        obj._subgroup = subgroup
        obj._get_subgroup_id()

        return obj

    def _get_subgroup_id(self):
        if self._subgroup:
            if not self.subgroups:
                self._parse_subgroups()
            try:
                self.subgroup_id = self.subgroups.index(self._subgroup)
            except ValueError:
                print("Invalid subgroup! Please try making request again")

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
        if isinstance(pair_tags[-1], str):
            pair_tags.pop()
        return day_name, pair_tags

    def _prepare_tags(self, tags):
        """Parses bs4 tags to list of Pair objects"""
        prepared_tags: list[Pair] = []
        for tag in tags:
            prepared_tags.append(
                Pair.from_tag(
                    tag,
                    subgroup_id=self.subgroup_id
                )
            )
        return prepared_tags

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
