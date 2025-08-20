from datetime import datetime
from datetime import timedelta

from pyremindkit import Priority
from pyremindkit import RemindKit

remind = RemindKit()

# Get the default calendar
default_calendar = remind.calendars.get_default()
print(f"Default calendar: {default_calendar.name}")

# List reminders due today or in the past that are incomplete
print("Incomplete reminders due today or in the past:")
for r in remind.get_reminders(due_before=datetime.now(), is_completed=False):
    print(f"- {r.title} (ID: {r.id}, Due: {r.due_date})")

# Create a new reminder
new_reminder = remind.create_reminder(
    title="Buy Milk",
    due_date=datetime.now(),
    notes="Get some oat milk too!",
    priority=Priority.HIGH,
    calendar_id=default_calendar.id,
)
print(f"Created reminder: {new_reminder.title} (ID: {new_reminder.id})")

print("Press Enter to continue...")
input()

# Move the reminder's due date 2 hours into the future
moved_reminder = remind.update_reminder(
    new_reminder.id,
    due_date=datetime.now() + timedelta(hours=2),
)
print(f"Moved reminder due date to: {moved_reminder.due_date}")

# Update the reminder's title
updated_reminder = remind.update_reminder(
    new_reminder.id,
    title="Buy Almond Milk Instead",
    notes="Changed my mind, get almond milk!",
)
print(f"Updated reminder title to: {updated_reminder.title}")
print(f"Updated reminder notes to: {updated_reminder.notes}")

print("Press Enter to continue...")
input()

# Get a reminder by ID
retrieved_reminder = remind.get_reminder_by_id(new_reminder.id)
print(f"Retrieved reminder: {retrieved_reminder.title}")

# Check for the next upcoming reminder
next_reminder = remind.get_next_reminder()
print(f"Next upcoming reminder: {next_reminder.title if next_reminder else 'None'}")

# Delete the reminder
remind.delete_reminder(new_reminder.id)
print(f"Deleted reminder: {new_reminder.title}")

# Verify the reminder was deleted
try:
    remind.get_reminder_by_id(new_reminder.id)
    print("Error: Reminder still exists!")
except ValueError:
    print("Verified: Reminder was successfully deleted")
