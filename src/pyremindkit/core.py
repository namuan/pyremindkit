from collections import defaultdict
from datetime import datetime
from threading import Event
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional

import objc
from EventKit import EKEntityTypeReminder
from EventKit import EKEventStore
from Foundation import NSCalendar
from Foundation import NSDate


class Reminder(NamedTuple):
    id: str  # Added id field to identify reminders
    title: str
    due_date: Optional[datetime]
    notes: Optional[str]
    completed: bool
    url: Optional[str]


class RemindersAPI:
    def __init__(self):
        self.event_store = self._grant_permission()

    def _grant_permission(self) -> EKEventStore:
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
            raise PermissionError("No access to reminder")

        return event_store

    def _convert_reminder(self, reminder) -> Reminder:
        # Convert NSDate to datetime if exists
        due_date = None
        if reminder.dueDateComponents():
            ns_date = reminder.dueDateComponents().date()
            if ns_date:
                due_date = datetime.fromtimestamp(ns_date.timeIntervalSince1970())

        return Reminder(
            id=reminder.calendarItemIdentifier(),  # Store the reminder's unique identifier
            title=reminder.title(),
            due_date=due_date,
            notes=reminder.notes(),
            completed=reminder.isCompleted(),
            url=reminder.URL(),
        )

    def _save_reminder(self, ek_reminder) -> bool:
        """
        Internal method to save changes to a reminder.

        Args:
            ek_reminder: The EKReminder object to save

        Returns:
            bool: True if save was successful

        Raises:
            RuntimeError: If saving fails
        """
        error = None
        success = self.event_store.saveReminder_commit_error_(ek_reminder, True, error)

        if not success:
            raise RuntimeError(f"Failed to update reminder: {error}")

        return success

    def get_all_calendars(self):
        """Get list of all reminder calendar names"""
        calendars = self.event_store.calendarsForEntityType_(EKEntityTypeReminder)
        return [calendar.title() for calendar in calendars]

    def get_incomplete_reminders(
        self, calendar_names: Optional[List[str]] = None
    ) -> Dict[str, List[Reminder]]:
        """
        Fetch incomplete reminders grouped by calendar

        Args:
            calendar_names: Optional list of calendar names to filter by. If None, fetches from all calendars.

        Returns:
            Dict with calendar names as keys and lists of Reminder objects as values
        """
        # Get all calendars or filter by provided names
        all_calendars = self.event_store.calendarsForEntityType_(EKEntityTypeReminder)
        if calendar_names:
            calendars = [cal for cal in all_calendars if cal.title() in calendar_names]
        else:
            calendars = all_calendars

        # Get end of today
        calendar = NSCalendar.currentCalendar()
        now = NSDate.date()
        end_date = calendar.dateBySettingHour_minute_second_ofDate_options_(
            23, 59, 59, now, 0
        )

        reminders_by_calendar = defaultdict(list)
        fetch_done = Event()

        def fetch_completion(reminders):
            if reminders:
                for reminder in reminders:
                    calendar_title = reminder.calendar().title()
                    reminders_by_calendar[calendar_title].append(
                        self._convert_reminder(reminder)
                    )
            fetch_done.set()

        # Get predicate for incomplete reminders
        predicate = self.event_store.predicateForIncompleteRemindersWithDueDateStarting_ending_calendars_(
            None,  # Starting date as None to include all past reminders
            end_date,  # End date as end of today
            calendars,
        )

        # Fetch reminders
        self.event_store.fetchRemindersMatchingPredicate_completion_(
            predicate, fetch_completion
        )
        fetch_done.wait(timeout=60)

        return dict(reminders_by_calendar)

    def pause_work(self, reminder: Reminder) -> Reminder:
        """
        Removes [WIP] prefix from the reminder title.

        :param reminder: Reminder object to pause
        :return: Updated reminder object
        """
        # Fetch the actual EKReminder object using the identifier
        ek_reminder = self.event_store.calendarItemWithIdentifier_(reminder.id)

        if not ek_reminder:
            raise ValueError("Reminder not found")

        current_title = ek_reminder.title()

        # Check if marked as WIP
        if current_title.startswith("[WIP]"):
            # Remove the [WIP] prefix and any extra spaces
            new_title = current_title.replace("[WIP]", "").strip()
            ek_reminder.setTitle_(new_title)
            self._save_reminder(ek_reminder)

        # Return updated reminder
        return self._convert_reminder(ek_reminder)

    def start_work(self, reminder: Reminder) -> Reminder:
        """
        Mark a reminder as work in progress by adding [WIP] prefix to its title

        Args:
            reminder: Reminder object to update

        Returns:
            Updated Reminder object
        """
        # Fetch the actual EKReminder object using the identifier
        ek_reminder = self.event_store.calendarItemWithIdentifier_(reminder.id)

        if not ek_reminder:
            raise ValueError("Reminder not found")

        current_title = ek_reminder.title()

        # Check if already marked as WIP
        if not current_title.startswith("[WIP]"):
            # Update the title with [WIP] prefix
            new_title = f"[WIP] {current_title}"
            ek_reminder.setTitle_(new_title)
            self._save_reminder(ek_reminder)

        # Return updated reminder
        return self._convert_reminder(ek_reminder)

    def complete_work(self, reminder: Reminder) -> Reminder:
        """
        Complete the work by setting the complete flag to True.
        Also removes [WIP] prefix if present.

        Args:
            reminder: Reminder object to complete

        Returns:
            Updated reminder object

        Raises:
            ValueError: If reminder not found
            RuntimeError: If saving fails
        """
        # Fetch the actual EKReminder object using the identifier
        ek_reminder = self.event_store.calendarItemWithIdentifier_(reminder.id)

        if not ek_reminder:
            raise ValueError("Reminder not found")

        # Set completion status to True
        ek_reminder.setCompleted_(True)

        # Remove [WIP] prefix if present
        current_title = ek_reminder.title()
        if current_title.startswith("[WIP]"):
            new_title = current_title.replace("[WIP]", "").strip()
            ek_reminder.setTitle_(new_title)

        # Save changes
        self._save_reminder(ek_reminder)

        # Return updated reminder
        return self._convert_reminder(ek_reminder)
