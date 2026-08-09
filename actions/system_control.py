"""
Bruno Assistant - System Control

Handles macOS system-level actions: volume, brightness, dark mode,
screen lock, battery status, Wi-Fi, Bluetooth, screenshots, and time.
"""

import os
import subprocess
from datetime import datetime


def set_volume(level: int) -> str:
    """Set the system output volume.

    Args:
        level: Volume level from 0 to 100.

    Returns:
        A string describing the result of the operation.
    """
    level = max(0, min(100, level))
    script = f"set volume output volume {level}"
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return f"Volume set to {level}%."
        else:
            return f"Failed to set volume: {result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return "Timed out trying to set volume."
    except Exception as e:
        return f"Error setting volume: {str(e)}"


def mute() -> str:
    """Mute the system audio output.

    Returns:
        A string describing the result of the operation.
    """
    script = "set volume output muted true"
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return "Audio muted."
        else:
            return f"Failed to mute audio: {result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return "Timed out trying to mute audio."
    except Exception as e:
        return f"Error muting audio: {str(e)}"


def unmute() -> str:
    """Unmute the system audio output.

    Returns:
        A string describing the result of the operation.
    """
    script = "set volume output muted false"
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return "Audio unmuted."
        else:
            return f"Failed to unmute audio: {result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return "Timed out trying to unmute audio."
    except Exception as e:
        return f"Error unmuting audio: {str(e)}"


def get_volume() -> str:
    """Get the current system output volume level.

    Returns:
        A string with the current volume level and mute status.
    """
    script = (
        "output volume of (get volume settings) & \",\" & "
        "output muted of (get volume settings)"
    )
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            parts = result.stdout.strip().split(",")
            volume = parts[0].strip() if len(parts) > 0 else "unknown"
            muted = parts[1].strip() if len(parts) > 1 else "unknown"
            mute_status = " (muted)" if muted == "true" else ""
            return f"Current volume: {volume}%{mute_status}."
        else:
            return f"Failed to get volume: {result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return "Timed out trying to get volume."
    except Exception as e:
        return f"Error getting volume: {str(e)}"


def set_brightness(level: int) -> str:
    """Set the display brightness.

    Requires the 'brightness' CLI tool (install via `brew install brightness`).
    Converts the 0-100 integer scale to a 0.0-1.0 float.

    Args:
        level: Brightness level from 0 to 100.

    Returns:
        A string describing the result of the operation.
    """
    level = max(0, min(100, level))
    brightness_float = level / 100.0
    try:
        result = subprocess.run(
            ["brightness", str(brightness_float)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return f"Brightness set to {level}%."
        else:
            error_msg = result.stderr.strip()
            return f"Failed to set brightness: {error_msg}"
    except FileNotFoundError:
        return (
            "The 'brightness' command-line tool is not installed. "
            "Install it with: brew install brightness"
        )
    except subprocess.TimeoutExpired:
        return "Timed out trying to set brightness."
    except Exception as e:
        return f"Error setting brightness: {str(e)}"


def toggle_dark_mode() -> str:
    """Toggle macOS dark mode on or off.

    Uses AppleScript to flip the current dark mode setting in System Events.

    Returns:
        A string describing the new dark mode state.
    """
    script = (
        'tell application "System Events"\n'
        "  tell appearance preferences\n"
        "    set dark mode to not dark mode\n"
        "    return dark mode\n"
        "  end tell\n"
        "end tell"
    )
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            is_dark = result.stdout.strip().lower() == "true"
            mode = "Dark Mode" if is_dark else "Light Mode"
            return f"Switched to {mode}."
        else:
            return f"Failed to toggle dark mode: {result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return "Timed out trying to toggle dark mode."
    except Exception as e:
        return f"Error toggling dark mode: {str(e)}"


def lock_screen() -> str:
    """Lock the macOS screen.

    Simulates the Cmd+Ctrl+Q keyboard shortcut using AppleScript.

    Returns:
        A string describing the result of the operation.
    """
    script = (
        'tell application "System Events" to keystroke "q" '
        "using {command down, control down}"
    )
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return "Screen locked."
        else:
            return f"Failed to lock screen: {result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return "Timed out trying to lock screen."
    except Exception as e:
        return f"Error locking screen: {str(e)}"


def get_battery() -> str:
    """Get the current battery status.

    Parses the output of `pmset -g batt` to extract battery percentage
    and charging state.

    Returns:
        A string with the current battery level and power status.
    """
    try:
        result = subprocess.run(
            ["pmset", "-g", "batt"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            output = result.stdout.strip()
            lines = output.split("\n")
            # First line contains power source info
            power_source = "Unknown"
            if "AC Power" in output:
                power_source = "AC Power (plugged in)"
            elif "Battery Power" in output:
                power_source = "Battery Power"
            # Second line typically contains percentage
            percentage = "unknown"
            charging_state = ""
            for line in lines:
                if "%" in line:
                    # Extract percentage (e.g., "85%")
                    parts = line.split("\t")
                    for part in parts:
                        if "%" in part:
                            # Parse "85%; charging;" or "85%; discharging;"
                            sub_parts = part.split(";")
                            percentage = sub_parts[0].strip()
                            if len(sub_parts) > 1:
                                charging_state = sub_parts[1].strip()
                            break
            status = f"Battery: {percentage}"
            if charging_state:
                status += f" ({charging_state})"
            status += f"\nPower source: {power_source}"
            return status
        else:
            return f"Failed to get battery info: {result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return "Timed out trying to get battery info."
    except Exception as e:
        return f"Error getting battery info: {str(e)}"


def toggle_wifi(state: str) -> str:
    """Turn Wi-Fi on or off.

    Uses networksetup to control the Wi-Fi interface.

    Args:
        state: Either 'on' or 'off'.

    Returns:
        A string describing the result of the operation.
    """
    state = state.lower().strip()
    if state not in ("on", "off"):
        return "Invalid state. Use 'on' or 'off'."
    try:
        result = subprocess.run(
            ["networksetup", "-setairportpower", "en0", state],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return f"Wi-Fi turned {state}."
        else:
            return f"Failed to toggle Wi-Fi: {result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return "Timed out trying to toggle Wi-Fi."
    except Exception as e:
        return f"Error toggling Wi-Fi: {str(e)}"


def take_screenshot(path: str = None) -> str:
    """Take a screenshot and save it to disk.

    Uses the macOS screencapture utility. Saves to the Desktop by default.

    Args:
        path: Optional file path to save the screenshot. Defaults to Desktop.

    Returns:
        A string describing where the screenshot was saved.
    """
    if path is None:
        desktop = os.path.expanduser("~/Desktop")
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        path = os.path.join(desktop, f"screenshot_{timestamp}.png")
    try:
        result = subprocess.run(
            ["screencapture", "-x", path],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return f"Screenshot saved to {path}."
        else:
            return f"Failed to take screenshot: {result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return "Timed out trying to take screenshot."
    except Exception as e:
        return f"Error taking screenshot: {str(e)}"


def get_current_time() -> str:
    """Get the current date and time.

    Returns:
        A formatted string with the current date, time, and day of the week.
    """
    now = datetime.now()
    return now.strftime("It's %A, %B %d, %Y at %I:%M %p.")


def toggle_bluetooth(state: str) -> str:
    """Turn Bluetooth on or off.

    Requires the 'blueutil' CLI tool (install via `brew install blueutil`).

    Args:
        state: Either 'on' or 'off'.

    Returns:
        A string describing the result of the operation.
    """
    state = state.lower().strip()
    if state not in ("on", "off"):
        return "Invalid state. Use 'on' or 'off'."
    flag = "1" if state == "on" else "0"
    try:
        result = subprocess.run(
            ["blueutil", "--power", flag],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return f"Bluetooth turned {state}."
        else:
            return f"Failed to toggle Bluetooth: {result.stderr.strip()}"
    except FileNotFoundError:
        return (
            "The 'blueutil' command-line tool is not installed. "
            "Install it with: brew install blueutil"
        )
    except subprocess.TimeoutExpired:
        return "Timed out trying to toggle Bluetooth."
    except Exception as e:
        return f"Error toggling Bluetooth: {str(e)}"
