"""Bruno AI Assistant — Rich Terminal UI.

A stunning terminal interface with a Peaky Blinders dark/gold aesthetic.
Uses the Rich library for panels, styled text, spinners, and layout.
"""

from __future__ import annotations

import time
from typing import Optional

from rich.align import Align
from rich.box import DOUBLE, HEAVY, ROUNDED, SIMPLE
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.style import Style
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

# ── Color Palette ────────────────────────────────────────────────────────────
GOLD = "#D4A84B"
AMBER = "#C19A2E"
DARK_GOLD = "#8B7330"
CREAM = "#F5E6C8"
SMOKE = "#3A3A3A"
CHARCOAL = "#1C1C1C"
WHISKEY = "#D4943A"
BLOOD_RED = "#8B0000"
STEEL = "#708090"

# ── Custom Theme ─────────────────────────────────────────────────────────────
BRUNO_THEME = Theme(
    {
        "gold": f"bold {GOLD}",
        "amber": f"{AMBER}",
        "dark_gold": f"{DARK_GOLD}",
        "cream": f"{CREAM}",
        "smoke": f"dim {SMOKE}",
        "whiskey": f"{WHISKEY}",
        "blood_red": f"bold {BLOOD_RED}",
        "steel": f"dim {STEEL}",
        "banner": f"bold {GOLD}",
        "status.listening": f"bold {GOLD}",
        "status.thinking": "bold #5B8DEF",
        "status.speaking": "bold #4CAF50",
        "status.waiting": f"dim {STEEL}",
        "status.error": f"bold {BLOOD_RED}",
        "user.msg": f"dim #5FAFAF",
        "bruno.msg": f"{CREAM}",
    }
)

# ── Status Configs ───────────────────────────────────────────────────────────
STATUS_CONFIGS: dict[str, dict] = {
    "listening": {
        "icon": "🎙️",
        "label": "Listening...",
        "style": f"bold {GOLD}",
        "border_style": GOLD,
        "spinner": "point",
    },
    "thinking": {
        "icon": "🧠",
        "label": "Thinking...",
        "style": "bold #5B8DEF",
        "border_style": "#5B8DEF",
        "spinner": "dots",
    },
    "speaking": {
        "icon": "🔊",
        "label": "Speaking...",
        "style": "bold #4CAF50",
        "border_style": "#4CAF50",
        "spinner": "dots",
    },
    "waiting": {
        "icon": "⏳",
        "label": "Waiting for wake word...",
        "style": f"dim {STEEL}",
        "border_style": STEEL,
        "spinner": "clock",
    },
    "error": {
        "icon": "⚠️",
        "label": "Error",
        "style": f"bold {BLOOD_RED}",
        "border_style": BLOOD_RED,
        "spinner": "dots",
    },
}

# ── ASCII Art Banner ─────────────────────────────────────────────────────────
BRUNO_BANNER = r"""
                           ████████████████
                        ██████████████████████
                     █████████████████████████████
                  ████████████████████████████████████
               ████████████████████████████████████████
              ███████████████████████████████████████████
             █████████████████████████████████████████████
            ██████████████████████████████████████████████
            ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
            ═══════════════════════════════════════════════

            ██████╗ ██████╗ ██╗   ██╗███╗  ██╗ ██████╗
            ██╔══██╗██╔══██╗██║   ██║████╗ ██║██╔═══██╗
            ██████╔╝██████╔╝██║   ██║██╔██╗██║██║   ██║
            ██╔══██╗██╔══██╗██║   ██║██║╚████║██║   ██║
            ██████╔╝██║  ██║╚██████╔╝██║ ╚███║╚██████╔╝
            ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚══╝ ╚═════╝

             A  I     V  O  I  C  E     A  S  S  I  S  T  A  N  T
            ───────────────────────────────────────────────
             By order of the Peaky Blinders.
"""


class BrunoUI:
    """Rich terminal UI for the Bruno AI Voice Assistant.

    Provides a visually stunning, Peaky Blinders–themed interface with
    gold/dark tones, status panels, styled messages, and ASCII art.
    """

    def __init__(self) -> None:
        self.console = Console(theme=BRUNO_THEME, highlight=False)

    # ── Banner ───────────────────────────────────────────────────────────
    def show_banner(self) -> None:
        """Display the Bruno ASCII art banner on startup."""
        banner_text = Text(BRUNO_BANNER, style=Style(color=GOLD, bold=True))
        banner_panel = Panel(
            Align.center(banner_text),
            box=DOUBLE,
            border_style=Style(color=DARK_GOLD),
            padding=(0, 2),
        )
        self.console.print()
        self.console.print(banner_panel)
        self.console.print()

    # ── Status ───────────────────────────────────────────────────────────
    def show_status(self, status: str) -> None:
        """Display a styled status panel.

        Args:
            status: One of 'listening', 'thinking', 'speaking', 'waiting', 'error'.
        """
        config = STATUS_CONFIGS.get(status)
        if config is None:
            config = STATUS_CONFIGS["waiting"]

        icon = config["icon"]
        label = config["label"]
        style = config["style"]
        border_style = config["border_style"]

        status_text = Text(f"  {icon}  {label}", style=style)
        panel = Panel(
            Align.center(status_text),
            box=ROUNDED,
            border_style=Style.parse(border_style),
            width=50,
            padding=(0, 1),
        )
        self.console.print(Align.center(panel))

    # ── User Message ─────────────────────────────────────────────────────
    def show_user_message(self, text: str) -> None:
        """Show what the user said.

        Args:
            text: The transcribed user speech.
        """
        user_text = Text()
        user_text.append("  🗣️  ", style="bold")
        user_text.append("You: ", style=f"bold {STEEL}")
        user_text.append(text, style=f"dim #5FAFAF")

        panel = Panel(
            user_text,
            box=ROUNDED,
            border_style=Style(color=STEEL, dim=True),
            padding=(0, 1),
        )
        self.console.print(panel)

    # ── Bruno Response ───────────────────────────────────────────────────
    def show_bruno_response(self, text: str) -> None:
        """Show Bruno's response with a gold double-bordered panel.

        Args:
            text: Bruno's response text.
        """
        response_text = Text()
        response_text.append("  🎩  ", style="bold")
        response_text.append("Bruno: ", style=f"bold {GOLD}")
        response_text.append(text, style=CREAM)

        panel = Panel(
            response_text,
            box=DOUBLE,
            border_style=Style(color=GOLD, bold=True),
            subtitle=f"[{DARK_GOLD}]── Peaky Blinders ──[/{DARK_GOLD}]",
            subtitle_align="center",
            padding=(1, 2),
        )
        self.console.print(panel)

    # ── Action ───────────────────────────────────────────────────────────
    def show_action(self, action_name: str, result: str) -> None:
        """Show an action that Bruno executed.

        Args:
            action_name: Name of the action (e.g., 'web_search', 'set_timer').
            result: The result or output of the action.
        """
        table = Table(
            show_header=True,
            header_style=f"bold {WHISKEY}",
            border_style=Style(color=WHISKEY),
            box=ROUNDED,
            title=f"[bold {WHISKEY}]⚡ Action Executed[/bold {WHISKEY}]",
            title_style=f"bold {WHISKEY}",
            padding=(0, 1),
        )
        table.add_column("Action", style=f"bold {GOLD}", min_width=18)
        table.add_column("Result", style=CREAM, min_width=40)
        table.add_row(action_name, result)

        self.console.print(table)

    # ── Error ────────────────────────────────────────────────────────────
    def show_error(self, error: str) -> None:
        """Show an error message in a red heavy-bordered panel.

        Args:
            error: The error message to display.
        """
        error_text = Text()
        error_text.append("  ⚠️  ", style="bold")
        error_text.append("Error: ", style=f"bold {BLOOD_RED}")
        error_text.append(error, style=f"italic {BLOOD_RED}")

        panel = Panel(
            error_text,
            box=HEAVY,
            border_style=Style(color=BLOOD_RED, bold=True),
            title=f"[bold {BLOOD_RED}]Something went wrong[/bold {BLOOD_RED}]",
            padding=(1, 2),
        )
        self.console.print(panel)

    # ── Startup Info ─────────────────────────────────────────────────────
    def show_startup_info(
        self,
        tts_engine: str,
        stt_model: str,
        wake_word: str,
    ) -> None:
        """Show configuration info at startup.

        Args:
            tts_engine: Active TTS engine name.
            stt_model: Active STT model name.
            wake_word: Wake word or 'disabled'.
        """
        table = Table(
            show_header=False,
            box=SIMPLE,
            padding=(0, 2),
            border_style=Style(color=DARK_GOLD),
        )
        table.add_column("Key", style=f"bold {STEEL}", min_width=16)
        table.add_column("Value", style=f"bold {CREAM}", min_width=28)

        table.add_row("🔊 TTS Engine", tts_engine)
        table.add_row("🎙️ STT Model", stt_model)
        table.add_row("👂 Wake Word", wake_word)

        info_panel = Panel(
            Align.center(table),
            box=DOUBLE,
            border_style=Style(color=AMBER),
            title=f"[bold {GOLD}]⚙️  Configuration[/bold {GOLD}]",
            subtitle=f"[{DARK_GOLD}]Bruno v1.0[/{DARK_GOLD}]",
            subtitle_align="center",
            padding=(1, 2),
        )
        self.console.print(Align.center(info_panel))

    # ── Clear ────────────────────────────────────────────────────────────
    def clear(self) -> None:
        """Clear the terminal screen."""
        self.console.clear()


# ── Demo ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    ui = BrunoUI()

    ui.clear()
    ui.show_banner()

    ui.show_startup_info(
        tts_engine="ElevenLabs (Adam)",
        stt_model="faster-whisper (base.en)",
        wake_word="Hey Bruno",
    )

    ui.console.print()
    ui.console.print(
        Rule(
            title=f"[{DARK_GOLD}]Live Demo[/{DARK_GOLD}]",
            style=DARK_GOLD,
        )
    )
    ui.console.print()

    # Show each status
    for status in ["waiting", "listening", "thinking", "speaking", "error"]:
        ui.show_status(status)
        time.sleep(0.4)

    ui.console.print()

    # User and Bruno interaction
    ui.show_user_message("What's the weather like in Birmingham today?")
    time.sleep(0.3)
    ui.show_bruno_response(
        "It's a cold, grey day in Birmingham — 7°C with overcast skies "
        "and a brisk wind from the northwest. Perfect weather for a "
        "whiskey by the fire, if you ask me."
    )

    ui.console.print()

    # Action
    ui.show_action(
        action_name="weather_lookup",
        result="Birmingham, UK — 7°C, Overcast, Wind NW 15 km/h",
    )

    ui.console.print()

    # Error
    ui.show_error(
        "Connection to ElevenLabs API timed out. Falling back to Edge TTS."
    )

    ui.console.print()
    ui.console.print(
        Align.center(
            Text(
                '"Big things have small beginnings." — Thomas Shelby',
                style=Style(color=DARK_GOLD, italic=True, dim=True),
            )
        )
    )
    ui.console.print()
