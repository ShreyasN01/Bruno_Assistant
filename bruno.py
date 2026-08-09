#!/usr/bin/env python3
"""
Bruno AI Assistant — Main Entry Point
"By order of Bruno."

A personal AI assistant for macOS with the voice and personality
of Thomas Shelby from Peaky Blinders. Activate with "Hey Bruno".

Usage:
    python bruno.py           # Start Bruno normally
    python bruno.py --test    # Test all modules without starting the loop
    python bruno.py --no-wake # Skip wake word, respond immediately (testing)
"""

import sys
import os
import signal
import argparse
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from ui.terminal_ui import BrunoUI


def test_modules(ui: BrunoUI) -> bool:
    """
    Test that all modules can be imported and initialized.
    
    Args:
        ui: BrunoUI instance for displaying results.
        
    Returns:
        True if all critical modules pass, False otherwise.
    """
    from rich.console import Console
    console = Console()
    
    all_passed = True
    
    console.print("\n[bold gold1]━━━ Module Tests ━━━[/bold gold1]\n")
    
    # Test config
    try:
        warnings = config.validate_config()
        console.print("  [green]✓[/green] config.py loaded")
        for w in warnings:
            console.print(f"    {w}")
    except Exception as e:
        console.print(f"  [red]✗[/red] config.py — {e}")
        all_passed = False
    
    # Test audio
    try:
        from core.audio import AudioRecorder, AudioPlayer, generate_activation_sound
        generate_activation_sound()
        console.print("  [green]✓[/green] core/audio.py — Audio system ready")
    except Exception as e:
        console.print(f"  [red]✗[/red] core/audio.py — {e}")
        all_passed = False
    
    # Test listener
    try:
        from core.listener import Listener
        console.print("  [green]✓[/green] core/listener.py — STT module importable")
    except Exception as e:
        console.print(f"  [red]✗[/red] core/listener.py — {e}")
        all_passed = False
    
    # Test brain
    try:
        from core.brain import BrunoBrain, TOOLS
        console.print(f"  [green]✓[/green] core/brain.py — {len(TOOLS)} tools defined")
    except Exception as e:
        console.print(f"  [red]✗[/red] core/brain.py — {e}")
        all_passed = False
    
    # Test speaker
    try:
        from core.speaker import Speaker
        console.print("  [green]✓[/green] core/speaker.py — TTS module importable")
    except Exception as e:
        console.print(f"  [red]✗[/red] core/speaker.py — {e}")
        all_passed = False
    
    # Test router
    try:
        from core.router import Router
        router = Router()
        actions = router.get_available_actions()
        console.print(f"  [green]✓[/green] core/router.py — {len(actions)} actions registered")
    except Exception as e:
        console.print(f"  [red]✗[/red] core/router.py — {e}")
        all_passed = False
    
    # Test wake word
    try:
        from core.wake_word import WakeWordDetector
        console.print("  [green]✓[/green] core/wake_word.py — Wake word module importable")
    except Exception as e:
        console.print(f"  [red]✗[/red] core/wake_word.py — {e}")
        all_passed = False
    
    # Test action modules
    action_modules = [
        "actions.app_launcher",
        "actions.system_control",
        "actions.web_search",
        "actions.media_control",
        "actions.messenger",
        "actions.calendar_manager",
        "actions.file_manager",
    ]
    
    for module_name in action_modules:
        try:
            __import__(module_name)
            console.print(f"  [green]✓[/green] {module_name.replace('.', '/')}.py")
        except Exception as e:
            console.print(f"  [red]✗[/red] {module_name.replace('.', '/')}.py — {e}")
            all_passed = False
    
    console.print()
    if all_passed:
        console.print("[bold green]All modules passed. Bruno is ready.[/bold green]\n")
    else:
        console.print("[bold red]Some modules failed. Check errors above.[/bold red]\n")
    
    return all_passed


def run_bruno(skip_wake_word: bool = False) -> None:
    """
    Main Bruno event loop.
    
    1. Initialize all modules
    2. Listen for wake word
    3. Record and transcribe command
    4. Process with AI brain
    5. Execute actions
    6. Speak response
    7. Loop back to step 2
    
    Args:
        skip_wake_word: If True, skips wake word detection (for testing).
    """
    ui = BrunoUI()
    
    # Clear screen and show banner
    ui.clear()
    ui.show_banner()
    
    # Validate config
    warnings = config.validate_config()
    critical_warnings = [w for w in warnings if "⚠️" in w]
    if critical_warnings:
        for w in critical_warnings:
            ui.show_error(w)
        ui.show_error("Please set up your .env file. Copy .env.example to .env and add your API keys.")
        sys.exit(1)
    
    # Initialize modules with status display
    ui.show_status("thinking")
    
    try:
        from core.speaker import Speaker
        speaker = Speaker()
    except Exception as e:
        ui.show_error(f"Failed to initialize speaker: {e}")
        sys.exit(1)
    
    try:
        from core.listener import Listener
        listener = Listener()
    except Exception as e:
        ui.show_error(f"Failed to initialize listener: {e}")
        sys.exit(1)
    
    try:
        from core.brain import BrunoBrain
        brain = BrunoBrain()
    except Exception as e:
        ui.show_error(f"Failed to initialize brain: {e}")
        sys.exit(1)
    
    try:
        from core.router import Router
        router = Router()
    except Exception as e:
        ui.show_error(f"Failed to initialize router: {e}")
        sys.exit(1)
    
    wake_word = None
    if not skip_wake_word:
        try:
            from core.wake_word import WakeWordDetector
            wake_word = WakeWordDetector()
        except Exception as e:
            ui.show_error(f"Failed to initialize wake word detector: {e}")
            ui.show_error("Running without wake word — press Enter to activate Bruno.")
    
    # Generate activation sounds
    from core.audio import generate_activation_sound, generate_deactivation_sound, AudioPlayer
    activate_sound = generate_activation_sound()
    deactivate_sound = generate_deactivation_sound()
    player = AudioPlayer()
    
    # Show startup info
    ui.show_startup_info(
        tts_engine=speaker.get_engine_info(),
        stt_model=listener.get_model_info(),
        wake_word=wake_word.get_detector_info() if wake_word else "Disabled (press Enter)"
    )
    
    # Startup greeting
    speaker.speak("Bruno is ready, sir. What do you need?")
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        ui.show_status("waiting")
        speaker.speak("Bruno signing off.")
        if wake_word:
            wake_word.cleanup()
        from core.audio import cleanup_temp_audio
        cleanup_temp_audio()
        ui.show_bruno_response("Until next time, mate. 🎩")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Main Event Loop
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    while True:
        try:
            # Step 1: Wait for wake word or Enter key
            if wake_word and not skip_wake_word:
                ui.show_status("waiting")
                wake_word.listen()
            elif skip_wake_word:
                ui.show_status("waiting")
                input("\n  Press Enter to speak to Bruno...\n")
            else:
                ui.show_status("waiting")
                input("\n  Press Enter to speak to Bruno...\n")
            
            # Play activation sound
            player.play_file(activate_sound, block=False)
            
            # Step 2: Listen and transcribe
            ui.show_status("listening")
            
            user_text = listener.listen()
            
            # Play deactivation sound
            player.play_file(deactivate_sound, block=False)
            
            if not user_text:
                ui.show_error("I didn't catch that. Say it again, mate.")
                speaker.speak("I didn't catch that.")
                continue
            
            # Display what user said
            ui.show_user_message(user_text)
            
            # Step 3: Process with AI brain
            ui.show_status("thinking")
            
            response_text, tool_calls = brain.process(user_text)
            
            # Step 4: Execute actions (if any)
            if tool_calls:
                results = router.execute(tool_calls)
                
                # Show each action
                for result in results:
                    ui.show_action(result["name"], str(result["result"]))
                
                # Get Bruno's verbal response after actions
                response_text = brain.get_response_after_actions(results)
            
            # Step 5: Speak and display response
            if response_text:
                ui.show_bruno_response(response_text)
                ui.show_status("speaking")
                speaker.speak(response_text)
        
        except KeyboardInterrupt:
            signal_handler(None, None)
        except Exception as e:
            ui.show_error(f"Something went sideways: {str(e)}")
            try:
                speaker.speak("Something went wrong. But we adapt. Always.")
            except Exception:
                pass


def main():
    """Parse arguments and run Bruno."""
    parser = argparse.ArgumentParser(
        description="Bruno — Your Personal AI Assistant 🎩",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python bruno.py              Start Bruno with wake word detection
  python bruno.py --no-wake    Start without wake word (press Enter to activate)
  python bruno.py --test       Test all modules
        """
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test all modules without starting the assistant"
    )
    parser.add_argument(
        "--no-wake",
        action="store_true",
        help="Skip wake word detection (press Enter to activate)"
    )
    
    args = parser.parse_args()
    
    ui = BrunoUI()
    
    if args.test:
        ui.clear()
        ui.show_banner()
        success = test_modules(ui)
        sys.exit(0 if success else 1)
    else:
        run_bruno(skip_wake_word=args.no_wake)


if __name__ == "__main__":
    main()
