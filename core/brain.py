"""
Bruno AI Assistant — AI Brain (LLM Integration)
Uses OpenAI GPT-4o-mini with function calling to understand commands
and route them to the appropriate action handlers.
"""

import json
from typing import Optional, Tuple, List, Dict, Any
from openai import OpenAI

import config


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Tool Definitions — All of Bruno's capabilities
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "open_application",
            "description": "Opens an application on the user's Mac. Use common app names like 'Safari', 'Spotify', 'Chrome', 'VS Code', 'Messages', 'Finder', 'Terminal', etc.",
            "parameters": {
                "type": "object",
                "required": ["app_name"],
                "properties": {
                    "app_name": {
                        "type": "string",
                        "description": "Name of the application to open (e.g., 'Safari', 'Spotify', 'Chrome')"
                    }
                },
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "close_application",
            "description": "Closes/quits an application on the user's Mac.",
            "parameters": {
                "type": "object",
                "required": ["app_name"],
                "properties": {
                    "app_name": {
                        "type": "string",
                        "description": "Name of the application to close"
                    }
                },
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_message",
            "description": "Sends an iMessage to a contact. The recipient can be a phone number, email, or contact name.",
            "parameters": {
                "type": "object",
                "required": ["recipient", "message"],
                "properties": {
                    "recipient": {
                        "type": "string",
                        "description": "Phone number, email address, or contact name of the recipient"
                    },
                    "message": {
                        "type": "string",
                        "description": "The message content to send"
                    }
                },
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Searches the web for a query. Opens Google search results in the default browser.",
            "parameters": {
                "type": "object",
                "required": ["query"],
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    }
                },
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_url",
            "description": "Opens a specific URL in the default web browser.",
            "parameters": {
                "type": "object",
                "required": ["url"],
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to open"
                    }
                },
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_volume",
            "description": "Sets the system volume to a specific level (0-100).",
            "parameters": {
                "type": "object",
                "required": ["level"],
                "properties": {
                    "level": {
                        "type": "integer",
                        "description": "Volume level from 0 to 100"
                    }
                },
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "mute_audio",
            "description": "Mutes the system audio.",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "unmute_audio",
            "description": "Unmutes the system audio.",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_brightness",
            "description": "Sets the screen brightness (0-100).",
            "parameters": {
                "type": "object",
                "required": ["level"],
                "properties": {
                    "level": {
                        "type": "integer",
                        "description": "Brightness level from 0 to 100"
                    }
                },
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "toggle_dark_mode",
            "description": "Toggles macOS dark mode on or off.",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "lock_screen",
            "description": "Locks the Mac screen.",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_battery_status",
            "description": "Gets the current battery level and charging status.",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "take_screenshot",
            "description": "Takes a screenshot and saves it to the Desktop.",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "toggle_wifi",
            "description": "Turns Wi-Fi on or off.",
            "parameters": {
                "type": "object",
                "required": ["state"],
                "properties": {
                    "state": {
                        "type": "string",
                        "enum": ["on", "off"],
                        "description": "Whether to turn Wi-Fi on or off"
                    }
                },
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "play_music",
            "description": "Starts playing music (resumes playback on Spotify or Apple Music).",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "pause_music",
            "description": "Pauses the currently playing music.",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "next_track",
            "description": "Skips to the next track in the music player.",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "previous_track",
            "description": "Goes back to the previous track in the music player.",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "play_specific_song",
            "description": "Searches for and plays a specific song, artist, or playlist on Spotify.",
            "parameters": {
                "type": "object",
                "required": ["query"],
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Song name, artist name, or playlist to search for and play"
                    }
                },
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_track",
            "description": "Gets information about the currently playing track (name, artist).",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_calendar_events",
            "description": "Gets today's calendar events from the Calendar app.",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_reminders",
            "description": "Gets the list of incomplete reminders.",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_reminder",
            "description": "Creates a new reminder in the Reminders app.",
            "parameters": {
                "type": "object",
                "required": ["title"],
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The reminder title/text"
                    },
                    "notes": {
                        "type": "string",
                        "description": "Optional notes for the reminder"
                    }
                },
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_files",
            "description": "Searches for files on the Mac using Spotlight search.",
            "parameters": {
                "type": "object",
                "required": ["query"],
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "File name or search term to look for"
                    }
                },
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_file",
            "description": "Opens a file or folder with its default application.",
            "parameters": {
                "type": "object",
                "required": ["path"],
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The full file path to open"
                    }
                },
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Gets the current date and time.",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        }
    },
]


class BrunoBrain:
    """
    The AI brain of Bruno — powered by OpenAI GPT-4o-mini with function calling.
    
    Processes natural language commands, determines which actions to take,
    and generates Thomas Shelby-style responses.
    """

    def __init__(self):
        if not config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required. Set it in your .env file.")
        
        self.client = OpenAI(
            api_key=config.OPENAI_API_KEY,
            base_url=getattr(config, "OPENAI_BASE_URL", None)
        )
        self.model = config.LLM_MODEL
        self.conversation_history: List[Dict[str, Any]] = []
        self.max_history = config.MAX_CONVERSATION_HISTORY

    def process(self, user_text: str) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Process a user's spoken command through the LLM.
        
        Uses function calling to determine what actions to take,
        then generates a natural language response in Bruno's voice.
        
        Args:
            user_text: The transcribed text from the user.
            
        Returns:
            Tuple of (response_text, tool_calls_list).
            - response_text: Bruno's verbal response string
            - tool_calls_list: List of dicts with 'name' and 'args' keys
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_text
        })
        
        # Trim history if too long
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]

        # Build messages with system prompt
        messages = [
            {"role": "system", "content": config.BRUNO_SYSTEM_PROMPT}
        ] + self.conversation_history

        try:
            # First call — may include tool calls
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                timeout=15
            )
            
            message = response.choices[0].message
            tool_calls_list = []
            
            if message.tool_calls:
                # Extract tool calls
                for tool_call in message.tool_calls:
                    func_name = tool_call.function.name
                    try:
                        args = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        args = {}
                    
                    tool_calls_list.append({
                        "name": func_name,
                        "args": args,
                        "id": tool_call.id
                    })
                
                # Store the assistant message with tool calls in history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": message.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in message.tool_calls
                    ]
                })
                
                return message.content or "", tool_calls_list
            else:
                # No tool calls — just a conversational response
                response_text = message.content or "..."
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response_text
                })
                return response_text, []
        
        except Exception as e:
            error_msg = f"My thoughts hit a wall. Error: {str(e)}"
            return error_msg, []

    def get_response_after_actions(self, tool_results: List[Dict[str, Any]]) -> str:
        """
        After actions are executed, get Bruno's final verbal response.
        
        This is called after the router executes the tool calls and
        returns their results. The LLM uses these results to generate
        a natural response.
        
        Args:
            tool_results: List of dicts with 'id', 'name', and 'result' keys.
            
        Returns:
            Bruno's verbal response string.
        """
        # Add tool results to conversation
        for result in tool_results:
            self.conversation_history.append({
                "role": "tool",
                "tool_call_id": result["id"],
                "content": str(result["result"])
            })

        # Build messages
        messages = [
            {"role": "system", "content": config.BRUNO_SYSTEM_PROMPT}
        ] + self.conversation_history

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            
            response_text = response.choices[0].message.content or "It's done."
            
            # Store in history
            self.conversation_history.append({
                "role": "assistant",
                "content": response_text
            })
            
            return response_text
        
        except Exception as e:
            return f"Action's done, but I lost my train of thought. Error: {str(e)}"

    def reset_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history = []

    def get_model_info(self) -> str:
        """Return info about the LLM model being used."""
        return f"OpenAI {self.model}"
