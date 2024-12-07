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
from typing import Dict, List

from pyremindkit import RemindersAPI, Reminder

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
```

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

### Fork the repository
Create your feature branch (git checkout -b feature/AmazingFeature)
Commit your changes (git commit -m 'Add some AmazingFeature')
Push to the branch (git push origin feature/AmazingFeature)
Open a Pull Request

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
