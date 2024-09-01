"""
Contains classes needed to get data
Like Faculty or Group, provides methods to get names, ids, etc.
"""

from urllib.parse import parse_qsl

from attrs import define
from bs4.element import Tag

from ontu_parser.classes.base import BaseClass


class BaseTag(BaseClass):
    """Base Tag Class for parsing BS4 tags from responses"""

    @classmethod
    def from_tag(cls, tag):
        """Checks tag and returns initialized object"""
        raise NotImplementedError("`from_tag` Not implemented")

    @staticmethod
    def _check_tag(tag: Tag):
        """Checks if tag is valid for usage"""
        raise NotImplementedError("`_check_tag` Not implemented")


@define
class Faculty(BaseTag):
    """Describes faculty from BS4 tag"""

    parent_id: int | None
    prefix: str
    faculty_tag: Tag

    @staticmethod
    def _check_tag(tag):
        attrs = getattr(tag, "attrs", None)
        span = getattr(tag, "span", None)
        required_properties = [attrs, span]
        if not all(required_properties):
            raise ValueError(f"Invalid tag: {tag}, has no attrs", tag)
        required = ["data-id"]
        for requirement in required:
            if requirement not in attrs:
                raise ValueError(
                    f"Invalid tag: {tag}, doesn't have attrs: {required}",
                    tag,
                    required,
                )
        span_string = getattr(span, "string", None)
        if span_string is None:
            raise ValueError(f"Invalid tag: {tag}, `span` has no string", tag)

    @classmethod
    def from_tag(
        cls,
        tag,
        prefix: str = "",
        parent_id: int | None = None,
    ):
        cls._check_tag(tag)
        return cls(
            faculty_tag=tag,
            prefix=prefix,
            parent_id=parent_id,
        )

    def get_faculty_picture(self):
        """Returns relative link to picture (if present)"""
        return self.faculty_tag.attrs.get("data-cover", None)

    def get_faculty_id(self):
        """Returns temporary id of faculty (for later use in search)"""
        return self.faculty_tag.attrs["data-id"]

    def get_faculty_name(self):
        """Returns name of the faculty"""
        return f"{self.prefix}{self.faculty_tag.span.string}"


@define
class Group(BaseTag):
    """Describes group from BS4 tag"""

    group_tag: Tag

    _icon_tag_filter = {"attrs": {"class": "icon"}}
    _text_tag_filter = {"attrs": {"class": "branding-bar"}}

    @staticmethod
    def _check_tag(tag):
        attrs = getattr(tag, "attrs", None)
        required = ["data-id"]
        for requirement in required:
            if requirement not in attrs:
                raise ValueError(
                    f"Invalid tag: {tag}, doesn't have attrs: {required}",
                    tag,
                    required,
                )

        # Children requiremenets

        icon = tag.find(**Group._icon_tag_filter)
        text = tag.find(**Group._text_tag_filter)
        required = [icon, text]
        if not all(required):
            raise ValueError(f"Invalid tag: {tag} doesn't have suitable children", tag)

    @classmethod
    def from_tag(cls, tag):
        cls._check_tag(tag)
        return cls(group_tag=tag)

    @property
    def text(self):
        """Returns text tag from group tag"""
        return self.group_tag.find(**self._text_tag_filter)

    @property
    def icon(self):
        """Returns icon tag from group tag"""
        return self.group_tag.find(**self._icon_tag_filter)

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
        attrs.pop("icon")
        return attrs[0]


class BaseStudentsLesson(BaseTag):
    """
    Describes lesson from bs4 tag

    Note: Lesson is a concrete even with date and teacher
    Pair on the other hand just states at which time lesson will happen
    """

    lesson_tag: Tag

    lesson_date: str = ""
    lesson_info: str = ""
    auditorium: str | None = None

    def __init__(self, *args, **kwargs):
        self.teacher: dict = {}
        self.lesson_name: dict = {}
        super().__init__(*args, **kwargs)

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


class StudentsRegularLesson(BaseStudentsLesson):
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
        lesson_top = self.lesson_tag.parent

        predm_element = lesson_top.find(name="span", attrs={"class": "predm"})
        self.lesson_name = {
            "short": predm_element.text,
            "full": predm_element.attrs.get("title", "Not Set"),
        }

        prp_element = lesson_top.find(name="span", attrs={"class": "prp"})
        self.teacher = {
            "short": prp_element.text.replace("\xa0", " "),  # Why...
            "full": prp_element.attrs.get("title", "Not Set"),
        }

        # Card tag consists of two children
        # First states type of content
        # Other - content itself
        card_tag = lesson_top.find(name="div", attrs={"class": "card"})
        if card_tag:
            card_content = card_tag.find(name="div", attrs={"class": "card-content"})
            if card_content:
                self.lesson_info = card_content.text.replace("\t", "").strip()

        auditorium_tag = lesson_top.find(name="a", attrs={"class": "fg-blue"})
        if auditorium_tag:
            self.auditorium = auditorium_tag.text


class StudentsPair(BaseTag):
    """
    Describes pair from bs4 tag

    Note: Pair describes when certain Lesson will happen
    """

    pair_tag: Tag

    pair_no: int = None
    _subgroup_id: int = 0

    def __init__(self, *args, **kwargs):
        self.lessons: list[BaseStudentsLesson] = []
        super().__init__(*args, **kwargs)

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
        pair_no_tag = self.pair_tag.find(attrs={"class": "lesson"})
        self.pair_no = int(pair_no_tag.text)

    def get_pair_tag_for_subgroup(self):
        """
        This method returns tag for this pair accounting for subgroup
        Currently opening a page for subgroup (like KN-321[a]) opens
        a page for both subgroups (or a group), thus we have to get a correct cell
        """
        pair_no_tag = self.pair_tag.find(attrs={"class": "lesson"})
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
        # All time 'days' have <span>s with dates in them
        all_dates = pair.find_all(name="span", attrs={"class": "fg-blue"})
        # There is at least one tag with this class if
        # there are lessons
        lesson = pair.find(attrs={"class": "predm"})
        lessons = []
        if not any([len(all_dates), lesson]):
            return lessons
        if len(all_dates) > 0:
            # This means we are dealing with 'all time' records
            # Which have multiple lessons per pair
            for lesson in all_dates:
                lessons.append(StudentsRegularLesson.from_tag(lesson))
            return lessons
        # This means we are dealing with single week records
        lessons.append(StudentsRegularLesson.from_tag(lesson))
        return lessons


class BaseSchedule(BaseTag):
    """Describes schedule from BS4 tag"""

    schedule_tag: Tag

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._schedule_data: dict[str, list["StudentsPair | TeachersPair"]] = {}

    @property
    def week(self):
        """Gets data for this week"""
        self._get_week()
        return self._schedule_data

    def _get_week(self):
        raise NotImplementedError("`_get_week` was not implemented")


class StudentsSchedule(BaseSchedule):
    """Describes schedule from HTML table"""

    subgroup_id: int = 0
    _subgroup: str = ""

    _splitter_class: str = "bg-darkCyan"

    def __init__(self, *args, **kwargs):
        self.subgroups: list[str] = []
        super().__init__(*args, **kwargs)

    @staticmethod
    def _check_tag(tag):
        if tag.name != "table":
            raise ValueError(f"Invalid tag: {tag}. Should be table", tag)

    @classmethod
    def from_tag(cls, tag, subgroup=None):
        cls._check_tag(tag)
        obj = cls()
        obj.schedule_tag = tag

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
        table_head = self.schedule_tag.thead
        head_rows = table_head.find_all(name="tr")

        # Hardcoding positions! Yikes!
        # head_rows[0] - meta info (`Day`, `Pair` columns, Group name)
        # head_rows[1] - sub_groups (a/b etc)

        sub_groups_tag = head_rows[1]
        sub_groups_tags = sub_groups_tag.find_all(name="th")

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
            if self._splitter_class in next_pair_tag.attrs.get("class", []):
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
        prepared_tags: list[StudentsPair] = []
        for tag in tags:
            prepared_tags.append(
                StudentsPair.from_tag(tag, subgroup_id=self.subgroup_id)
            )
        return prepared_tags

    def _get_week(self):
        """Iteratively loops trough table to get data for all days"""
        table_body = self.schedule_tag.tbody
        days = table_body.find_all(attrs={"class": "day"})
        for day in days:
            day_name, tags = self._prepare_day_tag(day)
            prepared_days = self._prepare_tags(tags)
            self._schedule_data[day_name] = prepared_days
        return self._schedule_data


class TeachersLesson:
    """Class to describe lesson for teachers"""

    # pylint: disable=too-few-public-methods

    name: str
    groups: str

    def __init__(self, name: str, groups: list[str] | str) -> None:
        self.name = name
        if isinstance(groups, list):
            self.groups = ", ".join(groups)
        else:
            self.groups = groups

    def __str__(self) -> str:
        return f"Lesson: {self.name} with ({self.groups})"


class TeachersPair(BaseTag):
    """Describes pair from bs4 tag"""

    __pair_no_not_specified = "Не вказано"
    __pair_name_not_specified = "Назва не вказана"
    __groups_not_specified = "Групи не вказані"

    pair_tag: Tag
    pair_no: int
    lesson: TeachersLesson | None

    @staticmethod
    def _check_tag(tag: Tag):
        pass

    def parse_tag(self):
        """This method parses bs4 and stores data from it in object's fields"""
        pair_no_text = self.pair_tag.attrs.get(
            "data-title-caption", self.__pair_no_not_specified
        )
        if pair_no_text != self.__pair_no_not_specified:
            self.pair_no = int(pair_no_text.split()[0])
        else:
            self.pair_no = 0

        pair_name_tag = self.pair_tag.find(name="p", attrs={"class": "text-leader"})
        pair_name = pair_name_tag.text.strip() if pair_name_tag else None

        groups_tag = self.pair_tag.find(name="p", attrs={"class": "text-secondary"})
        # Consider splitting. e.g of content: КН-341[а], КН-342[а], КН-343[а], КН-343[б]
        groups = groups_tag.text.strip() if groups_tag else None

        lesson = None
        if pair_name or groups:
            lesson = TeachersLesson(
                name=pair_name or self.__pair_name_not_specified,
                groups=groups or self.__groups_not_specified,
            )

        self.lesson = lesson

    @classmethod
    def from_tag(cls, tag):
        cls._check_tag(tag)
        obj = cls()
        obj.pair_tag = tag
        obj.parse_tag()
        return obj


class TeacherSchedule(BaseSchedule):
    """Describes schedule from HTML grid"""

    @staticmethod
    def _check_tag(tag: Tag):
        if tag.name != "div":
            raise ValueError(f"Invalid tag: {tag}. Should be div", tag)
        if "grid" not in tag.attrs.get("class", []):
            raise ValueError(f"Invalid tag: {tag}. Should be grid", tag)

    @classmethod
    def from_tag(cls, tag):
        cls._check_tag(tag)
        obj = cls()
        obj.schedule_tag = tag
        return obj

    def _prepare_day_tag(self, day_card: "Tag"):
        day_name = day_card.find(name="div", attrs={"class": "card-header"})
        if not day_name:
            raise ValueError(f"Invalid tag: {day_card}. No card-header found", day_card)
        day_name = day_name.text.strip()
        pairs = []
        for pair in day_card.find_all(name="div", attrs={"data-role": "panel"}):
            pairs.append(pair)
        return day_name, pairs

    def _prepare_tags(self, tags: list["Tag"]):
        prepared_tags: list[TeachersPair] = []
        for tag in tags:
            prepared_tags.append(TeachersPair.from_tag(tag))
        return prepared_tags

    def _get_week(self):
        all_cards = self.schedule_tag.find_all(name="div", attrs={"class": "card"})
        for card in all_cards:
            day_name, tags = self._prepare_day_tag(card)
            prepared_days = self._prepare_tags(tags)
            self._schedule_data[day_name] = prepared_days
        return self._schedule_data


@define
class Department(BaseTag):
    """Describes department from BS4 tag"""

    department: Tag

    @staticmethod
    def _check_tag(tag):
        attrs = getattr(tag, "attrs", None)
        span = tag.find(name="span", attrs={"class": "branding-bar"})
        required_properties = [attrs, span]
        if not all(required_properties):
            raise ValueError(f"Invalid tag: {tag}, has no attrs", tag)
        required = ["href"]
        for requirement in required:
            if requirement not in attrs:
                raise ValueError(
                    f"Invalid tag: {tag}, doesn't have attrs: {required}",
                    tag,
                    required,
                )
        span_string = getattr(span, "string", None)
        if span_string is None:
            raise ValueError(f"Invalid tag: {tag}, `span` has no string", tag)

    @classmethod
    def from_tag(cls, tag):
        cls._check_tag(tag)
        obj = cls(department=tag)
        if not obj.department:
            raise ValueError("Invalid tag", tag)
        return obj

    def get_department_picture(self):
        """Returns class of the picture (if present)"""
        container = self.department.find(name="div", attrs={"class": "slide-front"})
        if not container:
            return None
        span = container.find(name="span")
        if not span:
            return None
        return span.attrs.get("class", None)

    def get_department_link(self):
        """Returns (semi?) permanent relative link to department"""
        return self.department.attrs["href"]

    def get_department_id(self) -> int:
        """Return id of the department"""
        key_dict = dict(parse_qsl(self.get_department_link()))
        return int(key_dict["dep"])

    def get_department_name(self) -> dict[str, str]:
        """Returns name of the faculty"""
        name = {"short": "", "full": ""}
        short_name_span = self.department.find(
            name="span", attrs={"class": "branding-bar"}
        )
        full_name_span = self.department.find(name="div", attrs={"class": "slide-back"})
        name["short"] = short_name_span.text.strip() if short_name_span else ""
        full_name = full_name_span.text.strip() if full_name_span else ""
        name["full"] = full_name
        if full_name:
            words = full_name.split()
            name["full"] = " ".join(
                [x.capitalize() if len(x) > 2 else x for x in words]
            )
        return name


@define
class Teacher(BaseTag):
    """Describes teacher from BS4 tag"""

    teacher: Tag

    @staticmethod
    def _check_tag(tag):
        attrs = getattr(tag, "attrs", None)
        span = tag.find(name="span", attrs={"class": "branding-bar"})
        required_properties = [attrs, span]
        if not all(required_properties):
            raise ValueError(f"Invalid tag: {tag}, has no attrs", tag)
        required = ["href"]
        for requirement in required:
            if requirement not in attrs:
                raise ValueError(
                    f"Invalid tag: {tag}, doesn't have attrs: {required}",
                    tag,
                    required,
                )
        span_string = getattr(span, "string", None)
        if span_string is None:
            raise ValueError(f"Invalid tag: {tag}, `span` has no string", tag)

    @classmethod
    def from_tag(cls, tag):
        cls._check_tag(tag)
        obj = cls(teacher=tag)
        if not obj.teacher:
            raise ValueError("Invalid tag", tag)
        return obj

    def get_teacher_picture(self):
        """Returns class of the picture (if present)"""
        container = self.teacher.find(name="div", attrs={"class": "slide-front"})
        if not container:
            return None
        span = container.find(name="span")
        if not span:
            return None
        return span.attrs.get("class", None)

    def get_teacher_link(self):
        """Returns (semi?) permanent relative link to department"""
        return self.teacher.attrs["href"]

    def get_teacher_id(self) -> int:
        """Return id of teacher"""
        key_dict = dict(parse_qsl(self.get_teacher_link()))
        return int(key_dict["teacher"])

    def get_teacher_name(self) -> dict[str, str]:
        """Returns name of the faculty"""
        name = {"short": "", "full": ""}
        short_name_span = self.teacher.find(
            name="span", attrs={"class": "branding-bar"}
        )
        full_name_span = self.teacher.find(name="div", attrs={"class": "slide-back"})
        name["short"] = short_name_span.text.strip() if short_name_span else ""
        full_name = full_name_span.text.strip() if full_name_span else ""
        name["full"] = full_name
        if full_name:
            words = full_name.split()
            name["full"] = " ".join(
                [x.capitalize() if len(x) > 2 else x for x in words]
            )
        return name
