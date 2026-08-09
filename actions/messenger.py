"""
Bruno Assistant - Messenger

Handles sending iMessages and reading recent messages via AppleScript.
"""

import subprocess


def send_imessage(recipient: str, message: str) -> str:
    """Send an iMessage to a contact.

    Uses AppleScript to send a message through the Messages app.
    The recipient can be a phone number or email address.

    Args:
        recipient: Phone number or email of the recipient.
        message: The message text to send.

    Returns:
        A string describing the result of the operation.
    """
    # Escape double quotes for AppleScript string embedding
    escaped_message = message.replace('"', '\\"')
    escaped_recipient = recipient.replace('"', '\\"')
    script = (
        'tell application "Messages"\n'
        f'  set targetService to 1st account whose service type = iMessage\n'
        f'  set targetBuddy to participant "{escaped_recipient}" '
        f"of targetService\n"
        f'  send "{escaped_message}" to targetBuddy\n'
        "end tell"
    )
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode == 0:
            return f'Message sent to {recipient}: "{message}"'
        else:
            error_msg = result.stderr.strip()
            return f"Failed to send message to {recipient}: {error_msg}"
    except subprocess.TimeoutExpired:
        return "Timed out trying to send the message."
    except Exception as e:
        return f"Error sending message: {str(e)}"


def read_recent_messages(contact: str, count: int = 5) -> str:
    """Read recent messages from a contact.

    Note: Direct programmatic access to iMessage history is heavily
    restricted on macOS for privacy reasons. This function advises
    the user to check the Messages app directly.

    Args:
        contact: The contact name, phone number, or email.
        count: Number of recent messages to retrieve (default 5).

    Returns:
        A string advising the user to check Messages app.
    """
    return (
        f"Reading iMessage history for '{contact}' is restricted by macOS "
        "for privacy and security reasons. Please open the Messages app "
        "to view your recent conversations.\n\n"
        "Tip: You can say 'open Messages' and I'll launch the app for you."
    )
