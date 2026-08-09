"""
Bruno Assistant - Calendar Manager

Handles macOS Calendar events and Reminders via AppleScript.
"""

import subprocess


def _run_applescript(script: str) -> tuple[bool, str]:
    """Execute an AppleScript and return the result.

    Args:
        script: The AppleScript code to execute.

    Returns:
        A tuple of (success: bool, output_or_error: str).
    """
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "AppleScript timed out."
    except Exception as e:
        return False, str(e)


def get_todays_events() -> str:
    """Get today's calendar events from Calendar.app.

    Queries all calendars for events occurring today and returns
    their summary, start time, and end time.

    Returns:
        A formatted string listing today's events, or a status message.
    """
    script = (
        'set today to current date\n'
        'set hours of today to 0\n'
        'set minutes of today to 0\n'
        'set seconds of today to 0\n'
        'set tomorrow to today + (1 * days)\n'
        'set eventList to ""\n'
        'tell application "Calendar"\n'
        '  repeat with cal in calendars\n'
        '    set theEvents to (every event of cal whose '
        'start date >= today and start date < tomorrow)\n'
        '    repeat with evt in theEvents\n'
        '      set eventList to eventList & summary of evt & " | " & '
        '(start date of evt as string) & " - " & '
        '(end date of evt as string) & "\\n"\n'
        '    end repeat\n'
        '  end repeat\n'
        'end tell\n'
        'if eventList is "" then\n'
        '  return "No events scheduled for today."\n'
        'else\n'
        '  return eventList\n'
        'end if'
    )
    success, output = _run_applescript(script)
    if success:
        if output == "No events scheduled for today.":
            return output
        # Format the event list nicely
        events = [e.strip() for e in output.split("\n") if e.strip()]
        if not events:
            return "No events scheduled for today."
        formatted = "\n".join(f"  • {event}" for event in events)
        return f"Today's events ({len(events)}):\n{formatted}"
    return f"Failed to get today's events: {output}"


def get_reminders() -> str:
    """Get incomplete reminders from Reminders.app.

    Queries the default reminders list for items that are not yet completed.

    Returns:
        A formatted string listing incomplete reminders, or a status message.
    """
    script = (
        'tell application "Reminders"\n'
        '  set reminderList to ""\n'
        '  repeat with r in (reminders whose completed is false)\n'
        '    set reminderList to reminderList & name of r & "\\n"\n'
        '  end repeat\n'
        'end tell\n'
        'if reminderList is "" then\n'
        '  return "No incomplete reminders."\n'
        'else\n'
        '  return reminderList\n'
        'end if'
    )
    success, output = _run_applescript(script)
    if success:
        if output == "No incomplete reminders.":
            return output
        reminders = [r.strip() for r in output.split("\n") if r.strip()]
        if not reminders:
            return "No incomplete reminders."
        formatted = "\n".join(f"  • {r}" for r in reminders)
        return f"Incomplete reminders ({len(reminders)}):\n{formatted}"
    return f"Failed to get reminders: {output}"


def create_reminder(title: str, notes: str = "") -> str:
    """Create a new reminder in the default Reminders list.

    Args:
        title: The title of the reminder.
        notes: Optional notes to attach to the reminder.

    Returns:
        A string describing the result of the operation.
    """
    escaped_title = title.replace('"', '\\"')
    escaped_notes = notes.replace('"', '\\"')
    if notes:
        script = (
            'tell application "Reminders"\n'
            "  tell default list\n"
            f'    make new reminder with properties '
            f'{{name:"{escaped_title}", body:"{escaped_notes}"}}\n'
            "  end tell\n"
            "end tell"
        )
    else:
        script = (
            'tell application "Reminders"\n'
            "  tell default list\n"
            f'    make new reminder with properties '
            f'{{name:"{escaped_title}"}}\n'
            "  end tell\n"
            "end tell"
        )
    success, output = _run_applescript(script)
    if success:
        return f'Reminder created: "{title}"'
    return f"Failed to create reminder: {output}"
