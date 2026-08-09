"""
Bruno Assistant - Media Control

Handles music playback control for Spotify and Apple Music.
Uses AppleScript for media player interaction.
"""

import subprocess
import urllib.parse


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
            timeout=10,
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "AppleScript timed out."
    except Exception as e:
        return False, str(e)


def _is_app_running(app_name: str) -> bool:
    """Check whether a macOS application is currently running.

    Args:
        app_name: The exact name of the application.

    Returns:
        True if the application is running, False otherwise.
    """
    escaped = app_name.replace('"', '\\"')
    script = (
        f'tell application "System Events" to '
        f'(name of processes) contains "{escaped}"'
    )
    success, output = _run_applescript(script)
    return success and output.lower() == "true"


def play_music() -> str:
    """Start or resume music playback.

    Tries Spotify first; if not running, falls back to Apple Music.

    Returns:
        A string describing the result of the operation.
    """
    if _is_app_running("Spotify"):
        success, output = _run_applescript(
            'tell application "Spotify" to play'
        )
        if success:
            return "Resumed playback on Spotify."
        return f"Failed to play on Spotify: {output}"

    # Fall back to Apple Music
    success, output = _run_applescript('tell application "Music" to play')
    if success:
        return "Resumed playback on Apple Music."
    return f"Failed to play music: {output}"


def pause_music() -> str:
    """Pause the currently playing music.

    Tries Spotify first; if not running, falls back to Apple Music.

    Returns:
        A string describing the result of the operation.
    """
    if _is_app_running("Spotify"):
        success, output = _run_applescript(
            'tell application "Spotify" to pause'
        )
        if success:
            return "Paused Spotify."
        return f"Failed to pause Spotify: {output}"

    success, output = _run_applescript('tell application "Music" to pause')
    if success:
        return "Paused Apple Music."
    return f"Failed to pause music: {output}"


def next_track() -> str:
    """Skip to the next track.

    Tries Spotify first; if not running, falls back to Apple Music.

    Returns:
        A string describing the result of the operation.
    """
    if _is_app_running("Spotify"):
        success, output = _run_applescript(
            'tell application "Spotify" to next track'
        )
        if success:
            return "Skipped to next track on Spotify."
        return f"Failed to skip track on Spotify: {output}"

    success, output = _run_applescript(
        'tell application "Music" to next track'
    )
    if success:
        return "Skipped to next track on Apple Music."
    return f"Failed to skip track: {output}"


def previous_track() -> str:
    """Go back to the previous track.

    Tries Spotify first; if not running, falls back to Apple Music.

    Returns:
        A string describing the result of the operation.
    """
    if _is_app_running("Spotify"):
        success, output = _run_applescript(
            'tell application "Spotify" to previous track'
        )
        if success:
            return "Went back to previous track on Spotify."
        return f"Failed to go to previous track on Spotify: {output}"

    success, output = _run_applescript(
        'tell application "Music" to previous track'
    )
    if success:
        return "Went back to previous track on Apple Music."
    return f"Failed to go to previous track: {output}"


def get_current_track() -> str:
    """Get information about the currently playing track.

    Returns the track name and artist from Spotify or Apple Music.

    Returns:
        A string with the current track name and artist, or a status message.
    """
    if _is_app_running("Spotify"):
        script = (
            'tell application "Spotify"\n'
            "  if player state is playing then\n"
            '    return (name of current track) & " by " '
            "& (artist of current track)\n"
            "  else\n"
            '    return "Spotify is not currently playing."\n'
            "  end if\n"
            "end tell"
        )
        success, output = _run_applescript(script)
        if success:
            return f"Now playing: {output}"
        return f"Failed to get track info from Spotify: {output}"

    if _is_app_running("Music"):
        script = (
            'tell application "Music"\n'
            "  if player state is playing then\n"
            '    return (name of current track) & " by " '
            "& (artist of current track)\n"
            "  else\n"
            '    return "Apple Music is not currently playing."\n'
            "  end if\n"
            "end tell"
        )
        success, output = _run_applescript(script)
        if success:
            return f"Now playing: {output}"
        return f"Failed to get track info from Apple Music: {output}"

    return "No music player is currently running."


def play_specific(query: str) -> str:
    """Search and play a specific song or artist on Spotify.

    Opens a Spotify search URI which triggers a search in the Spotify app.

    Args:
        query: The song name, artist, or search query.

    Returns:
        A string describing the result of the operation.
    """
    try:
        encoded_query = urllib.parse.quote(query)
        uri = f"spotify:search:{encoded_query}"
        subprocess.run(
            ["open", uri],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return f"Searching Spotify for: {query}"
    except subprocess.TimeoutExpired:
        return "Timed out trying to search Spotify."
    except Exception as e:
        return f"Error searching Spotify: {str(e)}"


def set_music_volume(level: int) -> str:
    """Set the volume of the active music player.

    Adjusts volume in Spotify or Apple Music (scale 0–100).

    Args:
        level: Volume level from 0 to 100.

    Returns:
        A string describing the result of the operation.
    """
    level = max(0, min(100, level))

    if _is_app_running("Spotify"):
        success, output = _run_applescript(
            f'tell application "Spotify" to set sound volume to {level}'
        )
        if success:
            return f"Spotify volume set to {level}%."
        return f"Failed to set Spotify volume: {output}"

    success, output = _run_applescript(
        f'tell application "Music" to set sound volume to {level}'
    )
    if success:
        return f"Apple Music volume set to {level}%."
    return f"Failed to set music volume: {output}"
