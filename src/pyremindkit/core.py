from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from threading import Event
from typing import Callable
from typing import Generator
from typing import NamedTuple
from typing import Optional

import objc
from EventKit import EKEntityTypeReminder
from EventKit import EKEventStore
from EventKit import EKReminder
from Foundation import NSCalendar
from Foundation import NSCalendarUnitDay
from Foundation import NSCalendarUnitHour
from Foundation import NSCalendarUnitMinute
from Foundation import NSCalendarUnitMonth
from Foundation import NSCalendarUnitSecond
from Foundation import NSCalendarUnitYear
from Foundation import NSDate


# --- Data Classes ---
class Priority(Enum):
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class Reminder(NamedTuple):
    id: str  # Added id field to identify reminders
    title: str
    due_date: Optional[datetime]
    notes: Optional[str]
    completed: bool
    url: Optional[str]


@dataclass
class Calendar:
    id: str
    name: str
    owner: str  # Placeholder, as this isn't directly accessible via EventKit
    color: str
    is_default: bool = False
    _event_store: EKEventStore = None  # Internal reference to the event store

    def get_reminders(
        self,
        due_after: Optional[datetime] = None,
        due_before: Optional[datetime] = None,
        is_completed: Optional[bool] = None,
        priority: Optional[Priority] = None,
    ) -> Generator[Reminder, None, None]:
        """Fetches reminders from the calendar based on filters."""

        # Convert datetime objects to NSDate for the predicate
        due_start_date = (
            NSDate.dateWithTimeIntervalSince1970_(due_after.timestamp())
            if due_after
            else None
        )
        due_end_date = (
            NSDate.dateWithTimeIntervalSince1970_(due_before.timestamp())
            if due_before
            else None
        )

        # Get the EKCalendar object
        ek_calendar = self._event_store.calendarWithIdentifier_(self.id)

        if is_completed is None:
            # Fetch all reminders
            predicate = self._event_store.predicateForRemindersInCalendars_(
                [ek_calendar]
            )

        elif is_completed:
            # Fetch completed reminders within the date range
            predicate = self._event_store.predicateForCompletedRemindersWithCompletionDateStarting_ending_calendars_(
                due_start_date,
                due_end_date,
                [ek_calendar],
            )
        else:
            # Fetch incomplete reminders within the date range
            predicate = self._event_store.predicateForIncompleteRemindersWithDueDateStarting_ending_calendars_(
                due_start_date,
                due_end_date,
                [ek_calendar],
            )

        # Fetch the reminders
        fetch_done = Event()
        found_reminders = []

        def completion_handler(reminders, error=None):
            nonlocal found_reminders
            if reminders:
                found_reminders = reminders
            fetch_done.set()

        self._event_store.fetchRemindersMatchingPredicate_completion_(
            predicate, completion_handler
        )
        fetch_done.wait(timeout=60)

        for ek_reminder in found_reminders:
            # Apply priority filter if provided - EventKit priorities: 0 (none), 1-4 (low), 5 (medium), 6-9 (high)
            if priority == Priority.LOW and not (1 <= ek_reminder.priority() <= 4):
                continue
            if priority == Priority.MEDIUM and ek_reminder.priority() != 5:
                continue
            if priority == Priority.HIGH and not (6 <= ek_reminder.priority() <= 9):
                continue

            yield _convert_ek_reminder_to_reminder(ek_reminder)

    def create_reminder(self, **kwargs) -> Reminder:
        """Creates a new reminder in this calendar."""
        ek_calendar = self._event_store.calendarWithIdentifier_(self.id)

        # Create a new EKReminder object
        new_reminder = EKReminder.reminderWithEventStore_(self._event_store)
        new_reminder.setCalendar_(ek_calendar)

        new_reminder.setTitle_(kwargs.get("title", ""))

        if "due_date" in kwargs and kwargs["due_date"]:
            # Create NSDateComponents from datetime
            components = NSCalendar.currentCalendar().components_fromDate_(
                NSCalendarUnitYear
                | NSCalendarUnitMonth
                | NSCalendarUnitDay
                | NSCalendarUnitHour
                | NSCalendarUnitMinute
                | NSCalendarUnitSecond,  # Corrected usage
                NSDate.dateWithTimeIntervalSince1970_(kwargs["due_date"].timestamp()),
            )
            new_reminder.setDueDateComponents_(components)

        if "notes" in kwargs:
            new_reminder.setNotes_(kwargs["notes"])

        if "priority" in kwargs:
            if kwargs["priority"] == Priority.NONE:
                new_reminder.setPriority_(0)
            elif kwargs["priority"] == Priority.HIGH:
                new_reminder.setPriority_(1)
            elif kwargs["priority"] == Priority.MEDIUM:
                new_reminder.setPriority_(5)
            elif kwargs["priority"] == Priority.LOW:
                new_reminder.setPriority_(9)

        if "is_completed" in kwargs:
            new_reminder.setCompleted_(kwargs["is_completed"])

        if "url" in kwargs:
            new_reminder.setURL_(kwargs["url"])

        # Save the new reminder
        _save_ek_reminder(self._event_store, new_reminder)

        return _convert_ek_reminder_to_reminder(new_reminder)


class CalendarManager:
    def __init__(self, client, event_store: EKEventStore):
        self._client = client
        self._event_store = event_store

    def list(self) -> Generator[Calendar, None, None]:
        """Lists all calendars."""
        calendars = self._event_store.calendarsForEntityType_(EKEntityTypeReminder)
        for calendar in calendars:
            yield Calendar(
                id=calendar.calendarIdentifier(),
                name=calendar.title(),
                owner="Unknown",  # Owner information is not directly available in EventKit
                color=str(calendar.color()),
                is_default=calendar.isImmutable(),  # Best approximation for "default"
                _event_store=self._event_store,
            )

    def get(self, name: str) -> Calendar:
        """Gets a calendar by its name."""
        for calendar in self.list():
            if calendar.name == name:
                return calendar
        raise ValueError(f"Calendar with name '{name}' not found.")

    def get_by_id(self, id: str) -> Calendar:
        """Gets a calendar by its ID."""
        for calendar in self.list():
            if calendar.id == id:
                return calendar
        raise ValueError(f"Calendar with ID '{id}' not found.")

    def search(self, query: str) -> Generator[Calendar, None, None]:
        """Searches for calendars matching the query in their name."""
        for calendar in self.list():
            if query.lower() in calendar.name.lower():
                yield calendar

    def get_default(self) -> Calendar:
        """Gets the default calendar."""
        default_calendar = self._event_store.defaultCalendarForNewReminders()
        if default_calendar:
            return Calendar(
                id=default_calendar.calendarIdentifier(),
                name=default_calendar.title(),
                owner="Unknown",
                color=str(default_calendar.color()),
                is_default=True,
                _event_store=self._event_store,
            )
        raise ValueError("No default calendar found.")


class RemindKit:
    def __init__(self):
        self._event_store = _grant_permission()
        self.calendars = CalendarManager(self, self._event_store)
        self._is_authenticated = False
        self._on_reminder_created_callbacks = []
        self._on_reminder_completed_callbacks = []

    def authenticate(self) -> None:
        """Mark the client as authenticated"""
        self._is_authenticated = True

    def create_reminder(self, **kwargs) -> Reminder:
        """Creates a new reminder (in the default calendar if not specified)."""
        calendar_id = kwargs.pop("calendar_id", None)
        if calendar_id:
            calendar = self.calendars.get_by_id(calendar_id)
        else:
            calendar = self.calendars.get_default()

        reminder = calendar.create_reminder(**kwargs)

        for callback in self._on_reminder_created_callbacks:
            callback(reminder)

        return reminder

    def update_reminder(self, reminder_id: str, **kwargs) -> Reminder:
        """Updates an existing reminder with new attributes."""
        ek_reminder = self._event_store.calendarItemWithIdentifier_(reminder_id)
        if not ek_reminder:
            raise ValueError(f"Reminder with ID '{reminder_id}' not found.")

        if "title" in kwargs:
            ek_reminder.setTitle_(kwargs["title"])

        if "due_date" in kwargs and kwargs["due_date"]:
            components = NSCalendar.currentCalendar().components_fromDate_(
                NSCalendarUnitYear
                | NSCalendarUnitMonth
                | NSCalendarUnitDay
                | NSCalendarUnitHour
                | NSCalendarUnitMinute
                | NSCalendarUnitSecond,
                NSDate.dateWithTimeIntervalSince1970_(kwargs["due_date"].timestamp()),
            )
            ek_reminder.setDueDateComponents_(components)

        if "notes" in kwargs:
            ek_reminder.setNotes_(kwargs["notes"])

        if "priority" in kwargs:
            if kwargs["priority"] == Priority.NONE:
                ek_reminder.setPriority_(0)
            elif kwargs["priority"] == Priority.HIGH:
                ek_reminder.setPriority_(1)
            elif kwargs["priority"] == Priority.MEDIUM:
                ek_reminder.setPriority_(5)
            elif kwargs["priority"] == Priority.LOW:
                ek_reminder.setPriority_(9)

        if "is_completed" in kwargs:
            ek_reminder.setCompleted_(kwargs["is_completed"])

        if "url" in kwargs:
            ek_reminder.setURL_(kwargs["url"])

        _save_ek_reminder(self._event_store, ek_reminder)

        return _convert_ek_reminder_to_reminder(ek_reminder)

    def get_reminder_by_id(self, id: str) -> Reminder:
        """Gets a reminder by its ID."""
        ek_reminder = self._event_store.calendarItemWithIdentifier_(id)
        if ek_reminder:
            return _convert_ek_reminder_to_reminder(ek_reminder)
        raise ValueError(f"Reminder with ID '{id}' not found.")

    def get_reminders(
        self,
        due_after: Optional[datetime] = None,
        due_before: Optional[datetime] = None,
        is_completed: Optional[bool] = None,
        priority: Optional[Priority] = None,
        calendar_id: Optional[str] = None,
    ) -> Generator[Reminder, None, None]:
        """Gets reminders based on the provided filters."""
        if calendar_id:
            # Fetch reminders from a specific calendar
            calendar = self.calendars.get_by_id(calendar_id)
            yield from calendar.get_reminders(
                due_after, due_before, is_completed, priority
            )
        else:
            # Fetch reminders from all calendars
            for calendar in self.calendars.list():
                yield from calendar.get_reminders(
                    due_after, due_before, is_completed, priority
                )

    def search_reminders(self, query: str) -> Generator[Reminder, None, None]:
        """Searches for reminders matching the query in their title or notes."""
        for calendar in self.calendars.list():
            for reminder in calendar.get_reminders():
                if query.lower() in reminder.title.lower():
                    yield reminder
                elif reminder.notes and query.lower() in reminder.notes.lower():
                    yield reminder

    def delete_reminder(self, reminder_id: str) -> bool:
        """Deletes a reminder by its ID."""
        ek_reminder = self._event_store.calendarItemWithIdentifier_(reminder_id)
        if not ek_reminder:
            raise ValueError(f"Reminder with ID '{reminder_id}' not found.")

        error = None
        success = self._event_store.removeReminder_commit_error_(
            ek_reminder, True, error
        )

        if not success:
            raise RuntimeError(f"Failed to delete reminder: {error}")

        return success

    def on_reminder_created(self, callback: Callable) -> None:
        """Registers a callback to be called when a reminder is created."""
        self._on_reminder_created_callbacks.append(callback)

    def on_reminder_completed(self, callback: Callable) -> None:
        """Registers a callback to be called when a reminder is completed."""
        self._on_reminder_completed_callbacks.append(callback)


# --- Helper Functions ---


def _grant_permission() -> EKEventStore:
    """Grants permission to access reminders and returns the EKEventStore."""
    event_store = EKEventStore.alloc().init()
    done = Event()
    result = {}

    def completion_handler(granted: bool, error: objc.objc_object) -> None:
        result["granted"] = granted
        result["error"] = error
        done.set()

    event_store.requestFullAccessToRemindersWithCompletion_(completion_handler)
    done.wait(timeout=60)
    if not result.get("granted"):
        raise PermissionError("No access to reminders")

    return event_store


def _convert_ek_reminder_to_reminder(ek_reminder) -> Reminder:
    """Converts an EKReminder object to a Reminder object."""
    due_date = None
    if ek_reminder.dueDateComponents():
        ns_date = ek_reminder.dueDateComponents().date()
        if ns_date:
            due_date = datetime.fromtimestamp(ns_date.timeIntervalSince1970())

    return Reminder(
        id=ek_reminder.calendarItemIdentifier(),
        title=ek_reminder.title(),
        due_date=due_date,
        notes=ek_reminder.notes(),
        completed=ek_reminder.isCompleted(),
        url=str(ek_reminder.URL()) if ek_reminder.URL() else None,
    )


def _save_ek_reminder(event_store: EKEventStore, ek_reminder) -> bool:
    """Saves changes to an EKReminder."""
    error = None
    success = event_store.saveReminder_commit_error_(ek_reminder, True, error)

    if not success:
        raise RuntimeError(f"Failed to update reminder: {error}")

    return success
