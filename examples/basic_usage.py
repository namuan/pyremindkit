from typing import Dict
from typing import List

from pyremindkit import Reminder
from pyremindkit import RemindersAPI

# Create API instance
api = RemindersAPI()


# Usage example:
def print_reminders(reminders_dict: Dict[str, List[Reminder]]):
    for calendar_name, reminders in reminders_dict.items():
        print(f"\n=== {calendar_name} Calendar ===")
        for reminder in reminders:
            print(f"Title: {reminder.title}")
            print(f"ID: {reminder.id}")
            if reminder.due_date:
                print(f"Due Date: {reminder.due_date}")
            if reminder.notes:
                print(f"Notes: {reminder.notes}")
            if reminder.url:
                print(f"URL: {reminder.url}")
            print("---")


# Get all incomplete reminders
all_reminders = api.get_incomplete_reminders()
print_reminders(all_reminders)

# Example: Start work on the first reminder from any calendar
for calendar_reminders in all_reminders.values():
    if calendar_reminders:
        first_reminder = calendar_reminders[1]
        updated_reminder = api.pause_work(first_reminder)
        print("\nUpdated reminder:")
        print(f"Title: {updated_reminder.title}")
        break
