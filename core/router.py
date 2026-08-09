"""
Bruno AI Assistant — Command Router
Maps LLM tool calls to actual action handler functions and executes them.
"""

from typing import Dict, Any, List, Callable


class Router:
    """
    Routes tool calls from the AI brain to the appropriate action handlers.
    
    Each tool call from the LLM contains a function name and arguments.
    The router maps these to actual Python functions in the actions/ modules.
    """

    def __init__(self):
        self._routes: Dict[str, Callable] = {}
        self._register_all_routes()

    def _register_all_routes(self) -> None:
        """Register all action handlers from the actions/ modules."""
        try:
            from actions import app_launcher
            self._routes["open_application"] = lambda args: app_launcher.open_app(args["app_name"])
            self._routes["close_application"] = lambda args: app_launcher.close_app(args["app_name"])
        except ImportError as e:
            print(f"[Router] Warning: Could not load app_launcher: {e}")

        try:
            from actions import system_control
            self._routes["set_volume"] = lambda args: system_control.set_volume(args["level"])
            self._routes["mute_audio"] = lambda args: system_control.mute()
            self._routes["unmute_audio"] = lambda args: system_control.unmute()
            self._routes["set_brightness"] = lambda args: system_control.set_brightness(args["level"])
            self._routes["toggle_dark_mode"] = lambda args: system_control.toggle_dark_mode()
            self._routes["lock_screen"] = lambda args: system_control.lock_screen()
            self._routes["get_battery_status"] = lambda args: system_control.get_battery()
            self._routes["take_screenshot"] = lambda args: system_control.take_screenshot()
            self._routes["toggle_wifi"] = lambda args: system_control.toggle_wifi(args["state"])
            self._routes["get_current_time"] = lambda args: system_control.get_current_time()
        except ImportError as e:
            print(f"[Router] Warning: Could not load system_control: {e}")

        try:
            from actions import web_search
            self._routes["search_web"] = lambda args: web_search.search_web(args["query"])
            self._routes["open_url"] = lambda args: web_search.open_url(args["url"])
        except ImportError as e:
            print(f"[Router] Warning: Could not load web_search: {e}")

        try:
            from actions import media_control
            self._routes["play_music"] = lambda args: media_control.play_music()
            self._routes["pause_music"] = lambda args: media_control.pause_music()
            self._routes["next_track"] = lambda args: media_control.next_track()
            self._routes["previous_track"] = lambda args: media_control.previous_track()
            self._routes["play_specific_song"] = lambda args: media_control.play_specific(args["query"])
            self._routes["get_current_track"] = lambda args: media_control.get_current_track()
        except ImportError as e:
            print(f"[Router] Warning: Could not load media_control: {e}")

        try:
            from actions import messenger
            self._routes["send_message"] = lambda args: messenger.send_imessage(
                args["recipient"], args["message"]
            )
        except ImportError as e:
            print(f"[Router] Warning: Could not load messenger: {e}")

        try:
            from actions import calendar_manager
            self._routes["get_calendar_events"] = lambda args: calendar_manager.get_todays_events()
            self._routes["get_reminders"] = lambda args: calendar_manager.get_reminders()
            self._routes["create_reminder"] = lambda args: calendar_manager.create_reminder(
                args["title"], args.get("notes", "")
            )
        except ImportError as e:
            print(f"[Router] Warning: Could not load calendar_manager: {e}")

        try:
            from actions import file_manager
            self._routes["search_files"] = lambda args: file_manager.search_files(args["query"])
            self._routes["open_file"] = lambda args: file_manager.open_file(args["path"])
        except ImportError as e:
            print(f"[Router] Warning: Could not load file_manager: {e}")

    def execute(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute a list of tool calls and return their results.
        
        Args:
            tool_calls: List of dicts with 'name', 'args', and 'id' keys.
            
        Returns:
            List of dicts with 'id', 'name', and 'result' keys.
        """
        results = []
        
        for call in tool_calls:
            name = call["name"]
            args = call.get("args", {})
            call_id = call.get("id", "unknown")
            
            if name in self._routes:
                try:
                    result = self._routes[name](args)
                    results.append({
                        "id": call_id,
                        "name": name,
                        "result": result or "Action completed successfully."
                    })
                except Exception as e:
                    results.append({
                        "id": call_id,
                        "name": name,
                        "result": f"Error executing {name}: {str(e)}"
                    })
            else:
                results.append({
                    "id": call_id,
                    "name": name,
                    "result": f"Unknown action: {name}. This capability isn't available."
                })
        
        return results

    def get_available_actions(self) -> List[str]:
        """Return list of all registered action names."""
        return sorted(self._routes.keys())
