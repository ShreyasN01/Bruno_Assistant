"""
Bruno Assistant - Application Launcher

Handles opening, closing, and listing macOS applications.
Uses subprocess and AppleScript for system interaction.
"""

import subprocess

# Maps common fuzzy names to actual macOS application names
COMMON_APPS: dict[str, str] = {
    "chrome": "Google Chrome",
    "code": "Visual Studio Code",
    "vscode": "Visual Studio Code",
    "slack": "Slack",
    "notes": "Notes",
    "terminal": "Terminal",
    "finder": "Finder",
    "safari": "Safari",
    "spotify": "Spotify",
    "discord": "Discord",
    "messages": "Messages",
    "mail": "Mail",
    "photos": "Photos",
    "music": "Music",
    "maps": "Maps",
    "facetime": "FaceTime",
    "settings": "System Preferences",
    "preferences": "System Preferences",
    "zoom": "zoom.us",
    "teams": "Microsoft Teams",
    "word": "Microsoft Word",
    "excel": "Microsoft Excel",
    "firefox": "Firefox",
    "brave": "Brave Browser",
    "telegram": "Telegram",
    "whatsapp": "WhatsApp",
    "notion": "Notion",
    "figma": "Figma",
    "iterm": "iTerm",
    "warp": "Warp",
}


def open_app(app_name: str) -> str:
    """Open a macOS application by name.

    Resolves fuzzy names (e.g., 'chrome') to real app names using COMMON_APPS,
    then launches the application via subprocess.

    Args:
        app_name: The name of the application to open (fuzzy or exact).

    Returns:
        A string describing the result of the operation.
    """
    resolved_name = COMMON_APPS.get(app_name.lower().strip(), app_name)
    try:
        result = subprocess.run(
            ["open", "-a", resolved_name],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return f"Opened {resolved_name} successfully."
        else:
            error_msg = result.stderr.strip()
            return f"Failed to open {resolved_name}: {error_msg}"
    except subprocess.TimeoutExpired:
        return f"Timed out trying to open {resolved_name}."
    except Exception as e:
        return f"Error opening {resolved_name}: {str(e)}"


def close_app(app_name: str) -> str:
    """Close a running macOS application gracefully.

    Uses AppleScript to send a quit command to the specified application.

    Args:
        app_name: The name of the application to close (fuzzy or exact).

    Returns:
        A string describing the result of the operation.
    """
    resolved_name = COMMON_APPS.get(app_name.lower().strip(), app_name)
    escaped_name = resolved_name.replace('"', '\\"')
    script = f'tell application "{escaped_name}" to quit'
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return f"Closed {resolved_name} successfully."
        else:
            error_msg = result.stderr.strip()
            return f"Failed to close {resolved_name}: {error_msg}"
    except subprocess.TimeoutExpired:
        return f"Timed out trying to close {resolved_name}."
    except Exception as e:
        return f"Error closing {resolved_name}: {str(e)}"


def get_running_apps() -> str:
    """List all currently running macOS applications.

    Uses AppleScript to query the System Events process list for apps
    whose background-only property is false.

    Returns:
        A formatted string listing all running applications.
    """
    script = (
        'tell application "System Events" to get the name of every process '
        "whose background only is false"
    )
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            apps_raw = result.stdout.strip()
            if not apps_raw:
                return "No running applications found."
            apps = [app.strip() for app in apps_raw.split(",")]
            apps_list = "\n".join(f"  • {app}" for app in apps)
            return f"Running applications ({len(apps)}):\n{apps_list}"
        else:
            error_msg = result.stderr.strip()
            return f"Failed to list running apps: {error_msg}"
    except subprocess.TimeoutExpired:
        return "Timed out trying to list running apps."
    except Exception as e:
        return f"Error listing running apps: {str(e)}"
