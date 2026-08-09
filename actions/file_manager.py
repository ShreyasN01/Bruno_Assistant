"""
Bruno Assistant - File Manager

Handles file operations: opening files, revealing in Finder,
Spotlight search, and creating directories.
"""

import os
import subprocess


def open_file(path: str) -> str:
    """Open a file with its default application.

    Uses the macOS `open` command to launch the appropriate app.

    Args:
        path: The absolute or relative path to the file.

    Returns:
        A string describing the result of the operation.
    """
    expanded_path = os.path.expanduser(path)
    if not os.path.exists(expanded_path):
        return f"File not found: {expanded_path}"
    try:
        result = subprocess.run(
            ["open", expanded_path],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return f"Opened {expanded_path}."
        else:
            return f"Failed to open file: {result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return f"Timed out trying to open {expanded_path}."
    except Exception as e:
        return f"Error opening file: {str(e)}"


def reveal_in_finder(path: str) -> str:
    """Reveal a file or folder in Finder.

    Uses `open -R` to highlight the item in its parent Finder window.

    Args:
        path: The absolute or relative path to the file or folder.

    Returns:
        A string describing the result of the operation.
    """
    expanded_path = os.path.expanduser(path)
    if not os.path.exists(expanded_path):
        return f"Path not found: {expanded_path}"
    try:
        result = subprocess.run(
            ["open", "-R", expanded_path],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return f"Revealed {expanded_path} in Finder."
        else:
            return f"Failed to reveal in Finder: {result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return f"Timed out trying to reveal {expanded_path}."
    except Exception as e:
        return f"Error revealing in Finder: {str(e)}"


def search_files(query: str) -> str:
    """Search for files using macOS Spotlight (mdfind).

    Returns the top 10 matching file paths.

    Args:
        query: The search query string.

    Returns:
        A formatted string listing matching files, or a status message.
    """
    try:
        result = subprocess.run(
            ["mdfind", "-limit", "10", query],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode == 0:
            output = result.stdout.strip()
            if not output:
                return f"No files found matching '{query}'."
            files = output.split("\n")
            formatted = "\n".join(f"  {i+1}. {f}" for i, f in enumerate(files))
            return f"Search results for '{query}' ({len(files)} found):\n{formatted}"
        else:
            return f"Search failed: {result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return "Search timed out. Try a more specific query."
    except Exception as e:
        return f"Error searching files: {str(e)}"


def create_folder(path: str) -> str:
    """Create a new directory (including intermediate directories).

    Args:
        path: The absolute or relative path of the directory to create.

    Returns:
        A string describing the result of the operation.
    """
    expanded_path = os.path.expanduser(path)
    try:
        if os.path.exists(expanded_path):
            return f"Directory already exists: {expanded_path}"
        os.makedirs(expanded_path, exist_ok=True)
        return f"Created directory: {expanded_path}"
    except PermissionError:
        return f"Permission denied: cannot create {expanded_path}"
    except Exception as e:
        return f"Error creating directory: {str(e)}"
