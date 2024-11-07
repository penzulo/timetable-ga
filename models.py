from datetime import timedelta
from dataclasses import dataclass


class ClassTime:
    """
    Represents a specific class time, including the class ID, day, time, and duration.
    
    Attributes:
        class_id (str): The unique identifier for the class.
        day (str): The day of the week the class is held.
        time (str): The time of day the class is held.
        duration (timedelta): The duration of the class.
    """
    def __init__(self, class_id: str, day: str, time: str, duration: timedelta) -> None:
        self._id: str = class_id
        self._day: str = day
        self._time: str = time
        self._duration: timedelta = duration

    def __repr__(self) -> str:
        return f"ClassTime(id='{self._id}', day='{self._day}', time='{self._time}', duration='{self._duration}')"

    @property
    def class_id(self) -> str:
        return self._id

    @property
    def day(self) -> str:
        return self._day

    @property
    def time(self) -> str:
        return self._time

    @property
    def duration(self) -> timedelta:
        return self._duration


@dataclass(repr=True)
class Subject:
    subject_id: str
    name: str
    have_labs: bool

class Professor:
    def __init__(self, professor_id: str, name: str, subject: Subject) -> None:
        self._id: str = professor_id
        self._name: str = name
        self._subject: Subject = subject
        self._booked_times: list[ClassTime] = []

    def __repr__(self) -> str:
        return f'Professor(id="{self._id}", name="Dr. {self._name}", subject={self._subject})'

    @property
    def prof_id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def subject(self) -> Subject:
        return self._subject

    @property
    def booked_times(self) -> list[ClassTime]:
        return self._booked_times

    def book_professor(self, class_time: ClassTime):
        self._booked_times.append(class_time)

    def is_booked(self, class_time: ClassTime):
        return class_time in self._booked_times

class Room:
    def __init__(self, room_number: str) -> None:
        self._number: str = room_number
        self._booked_times: list[ClassTime] = []

    def __repr__(self) -> str:
        return f'Room(number="{self._number}", booked_times={self._booked_times})'

    @property
    def number(self) -> str:
        return self._number

    @property
    def booked_times(self) -> list[ClassTime]:
        return self._booked_times

    def book_room(self, class_time: ClassTime) -> None:
        self._booked_times.append(class_time)

    def is_booked(self, class_time: ClassTime):
        return class_time in self.booked_times

class Course:
    def __init__(
        self,
        number: str,
        name: str,
        subjects: list[Subject],
        professors: list[Professor],
        lectures_per_week: int,
        labs_per_week: int = 0,
    ) -> None:
        self._number: str = number
        self._name: str = name
        self._subjects: list[Subject] = subjects
        self._professors: list[Professor] = professors
        self._lectures_per_week: int = lectures_per_week
        self._labs_per_week: int = labs_per_week

    @property
    def course_number(self) -> str:
        return self._number

    @property
    def name(self) -> str:
        return self._name

    @property
    def professors(self) -> list[Professor]:
        return self._professors

    @property
    def subjects(self) -> list[Subject]:
        return self._subjects

    @property
    def lectures_per_week(self) -> int:
        return self._lectures_per_week

    @property
    def labs_per_week(self) -> int:
        return self._labs_per_week

    def is_subject_in_course(self, subject: Subject):
        return subject in self._subjects


class Department:
    """
    Represents a department within an educational institution, containing a collection of courses.
    
    Properties:
        name (str): The name of the department.
        courses (list[Course]): The list of courses offered by the department.
    """
    def __init__(self, name: str, courses: list[Course]):
        self._name: str = name
        self._courses: list[Course] = courses

    def __repr__(self) -> str:
        return f'Dept(name="{self._name}", courses="{self._courses}")'

    @property
    def name(self) -> str:
        return self._name

    @property
    def courses(self) -> list[Course]:
        return self._courses


class Division:
    """
    Represents a division with a name and a number of batches.
    
    Properties:
        name (str): The name of the division.
        num_batches (int): The number of batches in the division.
    """
    def __init__(self, name: str, num_batches: int):
        self._name: str = name
        self._num_batches: int = num_batches

    def __repr__(self) -> str:
        return f'Division(name="{self._name}", num_batches="{self._num_batches}")'

    @property
    def name(self) -> str:
        return self._name

    @property
    def num_batches(self) -> int:
        return self._num_batches
