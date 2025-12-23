"""
PyRemindKit - Comprehensive Feature Demonstration

This example demonstrates all features of PyRemindKit.
Created reminders are automatically cleaned up at the end.
Press Enter at each prompt to verify the action in Apple Reminders.
"""

from datetime import datetime
from datetime import timedelta

from pyremindkit import Priority
from pyremindkit import RemindKit

# Track all created reminders for cleanup
created_reminder_ids = []


def prompt(message):
    """Display a message and wait for user to press Enter."""
    print(f"\n{'=' * 60}")
    print(message)
    print("=" * 60)
    input("Press Enter to continue...")


def truncate_id(reminder_id, max_length=8):
    """Truncate a reminder ID for display purposes."""
    return reminder_id[:max_length]


# Initialize RemindKit
remind = RemindKit()
print("\n🚀 PyRemindKit Feature Demonstration\n")

# =============================================================================
# CALENDAR MANAGEMENT FEATURES
# =============================================================================
print("\n📅 CALENDAR MANAGEMENT FEATURES\n")

# Feature: Get default calendar
default_calendar = remind.calendars.get_default()
print(f"✓ Default calendar: {default_calendar.name}")

# Feature: List all calendars
print("\n✓ All available calendars:")
for cal in remind.calendars.list():
    print(f"  - {cal.name} (ID: {truncate_id(cal.id)}...)")

# Feature: Get calendar by name
try:
    calendar_by_name = remind.calendars.get(default_calendar.name)
    print(f"\n✓ Retrieved calendar by name: {calendar_by_name.name}")
except ValueError as e:
    print(f"  Could not get calendar by name: {e}")

# Feature: Get calendar by ID
calendar_by_id = remind.calendars.get_by_id(default_calendar.id)
print(f"✓ Retrieved calendar by ID: {calendar_by_id.name}")

# Feature: Search calendars
print("\n✓ Search calendars (searching for first word of default calendar):")
# Extract search term from calendar name
try:
    search_term = default_calendar.name.split()[0]
except IndexError:
    search_term = "Reminders"
for cal in remind.calendars.search(search_term):
    print(f"  - {cal.name}")

prompt("Review the calendar information above")

# =============================================================================
# REMINDER CREATION FEATURES
# =============================================================================
print("\n📝 REMINDER CREATION FEATURES\n")

# Feature: Create reminder with all attributes
reminder1 = remind.create_reminder(
    title="[Demo] Buy Groceries",
    due_date=datetime.now() + timedelta(hours=2),
    notes="Need milk, eggs, and bread",
    priority=Priority.HIGH,
    url="https://example.com/shopping-list",
    calendar_id=default_calendar.id,
)
created_reminder_ids.append(reminder1.id)
print(f"✓ Created HIGH priority reminder: {reminder1.title}")
print(f"  - Due: {reminder1.due_date}")
print(f"  - Notes: {reminder1.notes}")
print(f"  - URL: {reminder1.url}")
print(f"  - Priority: {reminder1.priority}")

prompt(
    "Check Apple Reminders - you should see '[Demo] Buy Groceries' with HIGH priority"
)

# Feature: Create reminders with different priority levels
reminder2 = remind.create_reminder(
    title="[Demo] Call dentist",
    due_date=datetime.now() + timedelta(days=1),
    priority=Priority.MEDIUM,
    calendar_id=default_calendar.id,
)
created_reminder_ids.append(reminder2.id)
print(f"\n✓ Created MEDIUM priority reminder: {reminder2.title}")

reminder3 = remind.create_reminder(
    title="[Demo] Water plants",
    due_date=datetime.now() + timedelta(days=2),
    priority=Priority.LOW,
    calendar_id=default_calendar.id,
)
created_reminder_ids.append(reminder3.id)
print(f"✓ Created LOW priority reminder: {reminder3.title}")

reminder4 = remind.create_reminder(
    title="[Demo] Read book",
    due_date=datetime.now() + timedelta(days=3),
    priority=Priority.NONE,
    calendar_id=default_calendar.id,
)
created_reminder_ids.append(reminder4.id)
print(f"✓ Created NONE priority reminder: {reminder4.title}")

prompt(
    "Check Apple Reminders - you should see all 4 demo reminders with different priorities"
)

# =============================================================================
# REMINDER RETRIEVAL AND FILTERING FEATURES
# =============================================================================
print("\n🔍 REMINDER RETRIEVAL AND FILTERING FEATURES\n")

# Feature: Get reminder by ID
retrieved = remind.get_reminder_by_id(reminder1.id)
print(f"✓ Retrieved reminder by ID: {retrieved.title}")

# Feature: List reminders with due_after filter
print("\n✓ Reminders due after now:")
for r in remind.get_reminders(due_after=datetime.now(), is_completed=False):
    if r.title.startswith("[Demo]"):
        print(f"  - {r.title} (Due: {r.due_date})")

# Feature: List reminders with due_before filter
print("\n✓ Reminders due before 2 days from now:")
for r in remind.get_reminders(
    due_before=datetime.now() + timedelta(days=2), is_completed=False
):
    if r.title.startswith("[Demo]"):
        print(f"  - {r.title} (Due: {r.due_date})")

# Feature: Filter reminders by priority
print("\n✓ HIGH priority reminders:")
for r in remind.get_reminders(priority=Priority.HIGH, is_completed=False):
    if r.title.startswith("[Demo]"):
        print(f"  - {r.title}")

# Feature: Filter reminders by calendar
print(f"\n✓ Reminders in calendar '{default_calendar.name}':")
for r in remind.get_reminders(calendar_id=default_calendar.id, is_completed=False):
    if r.title.startswith("[Demo]"):
        print(f"  - {r.title}")

# Feature: Search reminders by text
print("\n✓ Search reminders containing 'Demo':")
for r in remind.search_reminders("Demo"):
    if r.title.startswith("[Demo]"):
        print(f"  - {r.title}")

# Feature: Get next upcoming reminder
next_reminder = remind.get_next_reminder()
print(f"\n✓ Next upcoming reminder: {next_reminder.title if next_reminder else 'None'}")

prompt("Review the filtered reminder lists above")

# =============================================================================
# REMINDER UPDATE FEATURES
# =============================================================================
print("\n✏️ REMINDER UPDATE FEATURES\n")

# Feature: Update reminder title and notes
updated1 = remind.update_reminder(
    reminder1.id,
    title="[Demo] Buy Organic Groceries",
    notes="Updated: Need organic milk, free-range eggs, and whole wheat bread",
)
print(f"✓ Updated title: {updated1.title}")
print(f"  Updated notes: {updated1.notes}")

prompt(
    "Check Apple Reminders - '[Demo] Buy Groceries' should now be '[Demo] Buy Organic Groceries'"
)

# Feature: Update reminder due date
updated2 = remind.update_reminder(
    reminder1.id,
    due_date=datetime.now() + timedelta(hours=4),
)
print(f"\n✓ Updated due date: {updated2.due_date}")

# Feature: Update reminder priority
updated3 = remind.update_reminder(
    reminder2.id,
    priority=Priority.HIGH,
)
print(f"\n✓ Updated priority of '{reminder2.title}' from MEDIUM to HIGH")

# Feature: Update reminder URL
updated4 = remind.update_reminder(
    reminder1.id,
    url="https://example.com/organic-shopping",
)
print(f"\n✓ Updated URL: {updated4.url}")

# Feature: Mark reminder as completed
updated5 = remind.update_reminder(
    reminder4.id,
    is_completed=True,
)
print(f"\n✓ Marked as completed: {reminder4.title}")

prompt(
    "Check Apple Reminders - verify all updates (title, due date, priority, URL, completion)"
)

# Feature: List completed reminders
print("\n✓ Completed demo reminders:")
for r in remind.get_reminders(is_completed=True):
    if r.title.startswith("[Demo]"):
        print(f"  - {r.title} (Completed: {r.completed})")

# =============================================================================
# EVENT CALLBACK FEATURES
# =============================================================================
print("\n🔔 EVENT CALLBACK FEATURES\n")


# Feature: Register callback for reminder creation
def on_created(reminder):
    print(f"  → Callback triggered! Created: {reminder.title}")


remind.on_reminder_created(on_created)
print("✓ Registered on_reminder_created callback")

# Create a reminder to trigger the callback
reminder5 = remind.create_reminder(
    title="[Demo] Callback Test",
    due_date=datetime.now() + timedelta(hours=1),
    calendar_id=default_calendar.id,
)
created_reminder_ids.append(reminder5.id)

prompt("Notice the callback message above when the reminder was created")

# =============================================================================
# CLEANUP - Delete all created reminders
# =============================================================================
print("\n🧹 CLEANUP - Deleting all demo reminders\n")

for reminder_id in created_reminder_ids:
    try:
        remind.delete_reminder(reminder_id)
        print(f"✓ Deleted reminder (ID: {truncate_id(reminder_id)}...)")
    except (ValueError, RuntimeError) as e:
        print(f"✗ Could not delete reminder {truncate_id(reminder_id)}...: {e}")

# Verify cleanup
print("\n✓ Verifying all demo reminders are deleted...")
remaining = []
# Use search to efficiently find any remaining demo reminders
for r in remind.search_reminders("[Demo]"):
    remaining.append(r.title)

if remaining:
    print(f"⚠️ Warning: {len(remaining)} demo reminders still exist:")
    for title in remaining:
        print(f"  - {title}")
else:
    print("✓ All demo reminders successfully deleted!")

prompt("Check Apple Reminders - all [Demo] reminders should be gone")

print("\n✅ Feature demonstration complete!\n")
