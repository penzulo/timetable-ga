from datetime import timedelta


class Professor:
    def __init__(self, professor_id: str, name: str) -> None:
        self._id: str = professor_id
        self._name: str = name

    def get_id(self) -> str:
        return self._id

    def get_name(self) -> str:
        return self._name


class Room:
    def __init__(self, number: str) -> None:
        self._number: str = number

    def get_number(self) -> str:
        return self._number


class ClassTime:
    def __init__(self, class_id: str, day: str, time: str, duration: timedelta) -> None:
        self._id: str = class_id
        self._day: str = day
        self._time: str = time
        self._duration: timedelta = duration

    def get_id(self) -> str:
        return self._id

    def get_day(self) -> str:
        return self._day

    def get_time(self) -> str:
        return self._time

    def get_duration(self) -> timedelta:
        return self._duration


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

    def get_number(self) -> str:
        return self._number

    def get_name(self) -> str:
        return self._name

    def get_professors(self) -> list[Professor]:
        return self._professors

    def get_lectures_per_week(self) -> int:
        return self._lectures_per_week

    def get_labs_per_week(self) -> int:
        return self._labs_per_week


class Department:
    def __init__(self, name: str, courses: list[Course]):
        self._name: str = name
        self._courses: list[Course] = courses

    def get_name(self) -> str:
        return self._name

    def get_courses(self) -> list[Course]:
        return self._courses


class Panel:
    def __init__(self, name: str, num_batches: int):
        self._name: str = name
        self._num_batches: int = num_batches

    def get_name(self) -> str:
        return self._name

    def get_num_batches(self) -> int:
        return self._num_batches
