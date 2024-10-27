from datetime import timedelta


class ClassTime:
    def __init__(self, class_id: str, day: str, time: str, duration: timedelta) -> None:
        self._id: str = class_id
        self._day: str = day
        self._time: str = time
        self._duration: timedelta = duration

    def __str__(self) -> str:
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


class Professor:
    def __init__(self, professor_id: str, name: str) -> None:
        self._id: str = professor_id
        self._name: str = name
        self._available_times: list[ClassTime] = []

    def __str__(self) -> str:
        return f'Professor(id="{self._id}", name="{self._name}", available_times={self._available_times})'

    @property
    def prof_id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def available_times(self) -> list[ClassTime]:
        return self._available_times

    @available_times.setter
    def available_times(self, slots: list[ClassTime]) -> None:
        self._available_times = slots


class Room:
    def __init__(self, room_number: str) -> None:
        self._number: str = room_number

    def __str__(self) -> str:
        return f'Room(number="{self._number}")'

    @property
    def number(self) -> str:
        return self._number


class Course:
    def __init__(
        self,
        number: str,
        name: str,
        professors: list[Professor],
        lectures_per_week: int,
        labs_per_week: int = 0,
    ) -> None:
        self._number: str = number
        self._name: str = name
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
    def lectures_per_week(self) -> int:
        return self._lectures_per_week

    @property
    def labs_per_week(self) -> int:
        return self._labs_per_week


class Department:
    def __init__(self, name: str, courses: list[Course]):
        self._name: str = name
        self._courses: list[Course] = courses

    def __str__(self) -> str:
        return f'Dept(name="{self._name}", courses="{self._courses}")'

    @property
    def name(self) -> str:
        return self._name

    @property
    def courses(self) -> list[Course]:
        return self._courses


class Panel:
    def __init__(self, name: str, num_batches: int):
        self._name: str = name
        self._num_batches: int = num_batches

    def __str__(self) -> str:
        return f'Panel(name="{self._name}", num_batches="{self._num_batches}")'

    @property
    def name(self) -> str:
        return self._name

    @property
    def num_batches(self) -> int:
        return self._num_batches
