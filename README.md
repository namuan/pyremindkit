# PyRemindKit

A Python package that a simple wrapper over Apple Reminders API

## Features

WIP

## Installation

```shell
python3 -m pip install git+https://github.com/namuan/pyremindkit
```

## Quick Start

### Basic Usage

```python
from datetime import datetime

from pyremindkit import RemindKit, Priority

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
    calendar_id=default_calendar.id
)
print(f"Created reminder: {new_reminder.title} (ID: {new_reminder.id})")

# Update the reminder's title
updated_reminder = remind.update_reminder(
    new_reminder.id,
    title="Buy Almond Milk Instead",
    notes="Changed my mind, get almond milk!"
)
print(f"Updated reminder title to: {updated_reminder.title}")
print(f"Updated reminder notes to: {updated_reminder.notes}")

# Get a reminder by ID
retrieved_reminder = remind.get_reminder_by_id(new_reminder.id)
print(f"Retrieved reminder: {retrieved_reminder.title}")

remind.delete_reminder(new_reminder.id)
print(f"Deleted reminder: {new_reminder.title}")

# Verify the reminder was deleted
try:
    remind.get_reminder_by_id(new_reminder.id)
    print("Error: Reminder still exists!")
except ValueError:
    print("Verified: Reminder was successfully deleted")
```

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

### Fork the repository
* Create your feature branch (git checkout -b feature/AmazingFeature)
* Commit your changes (git commit -m 'Add some AmazingFeature')
* Push to the branch (git push origin feature/AmazingFeature)
* Open a Pull Request

## Development Setup

```shell
# Clone the repository
git clone https://github.com/namuan/pyremindkit.git
cd pyremindkit

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements/requirements-dev.txt
```

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Support
If you encounter any problems or have suggestions, please open an issue.
