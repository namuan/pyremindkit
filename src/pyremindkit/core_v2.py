from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Callable
from typing import Generator
from typing import List
from typing import Optional


class Priority(Enum):
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class RecurrenceType(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


@dataclass
class Location:
    name: str
    latitude: float
    longitude: float
    radius: float = 50.0


@dataclass
class Recurrence:
    type: RecurrenceType
    interval: int = 1
    end_date: Optional[datetime] = None
    days: Optional[List[str]] = None


@dataclass
class Reminder:
    id: str
    title: str
    calendar_id: str
    created_date: datetime
    modified_date: datetime
    due_date: Optional[datetime] = None
    notes: Optional[str] = None
    priority: Priority = Priority.NONE
    is_completed: bool = False
    recurrence: Optional[Recurrence] = None
    location: Optional[Location] = None
    tags: List[str] = None
    url: Optional[str] = None
    attachments: List[str] = None

    def update(self, **kwargs) -> None: ...

    def delete(self) -> None: ...

    def mark_complete(self) -> None: ...

    def mark_incomplete(self) -> None: ...

    def add_attachment(self, file_path: str) -> None: ...

    def get_attachments(self) -> List[str]: ...


@dataclass
class Calendar:
    id: str
    name: str
    owner: str
    color: str
    is_default: bool = False

    def get_reminders(self) -> Generator[Reminder, None, None]: ...

    def create_reminder(self, **kwargs) -> Reminder: ...


class CalendarManager:
    def __init__(self, client):
        self._client = client

    def list(self) -> Generator[Calendar, None, None]: ...

    def get(self, name: str) -> Calendar: ...

    def get_by_id(self, id: str) -> Calendar: ...

    def search(self, query: str) -> Generator[Calendar, None, None]: ...

    def get_default(self) -> Calendar: ...


class RemindKit:
    def __init__(self):
        self.calendars = CalendarManager(self)
        self._is_authenticated = False

    def authenticate(self) -> None:
        """Mark the client as authenticated"""
        self._is_authenticated = True

    def create_reminder(self, **kwargs) -> Reminder: ...

    def get_reminder_by_id(self, id: str) -> Reminder: ...

    def get_reminders(self, **filters) -> Generator[Reminder, None, None]: ...

    def search_reminders(self, query: str) -> Generator[Reminder, None, None]: ...

    def on_reminder_created(self, callback: Callable) -> None: ...

    def on_reminder_completed(self, callback: Callable) -> None: ...


if __name__ == "__main__":
    remind = RemindKit()
    remind.authenticate()  # Called after external authentication is successful

    # Iterate through reminders
    for reminder in remind.get_reminders(due_after=datetime.now()):
        print(reminder.title)

    # Search calendars
    for calendar in remind.calendars.search("Work"):
        # Get reminders from each calendar
        for reminder in calendar.get_reminders():
            print(reminder)
