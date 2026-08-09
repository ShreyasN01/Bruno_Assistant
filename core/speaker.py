"""
Bruno AI Assistant — Text-to-Speech (Speaker)
Gives Bruno his deep, commanding Thomas Shelby voice.

Supports three TTS engines with automatic fallback:
1. ElevenLabs — Premium deep voice (requires API key)
2. Edge TTS — Free, high-quality deep voice (requires internet)
3. macOS say — Offline fallback with Daniel voice (British)
"""

import os
import asyncio
import subprocess
from typing import Optional

import config
from core.audio import AudioPlayer, get_temp_audio_path


class Speaker:
    """
    Text-to-Speech engine for Bruno.
    
    Automatically selects the best available TTS engine based on
    configured API keys and preferences. Produces a deep, commanding
    voice inspired by Thomas Shelby.
    """

    def __init__(self):
        self.engine = config.get_tts_engine()
        self.player = AudioPlayer()
        self._phrase_cache: dict[str, str] = {}
        
        # Validate engine availability
        if self.engine == "elevenlabs":
            try:
                from elevenlabs.client import ElevenLabs
                self.eleven_client = ElevenLabs(api_key=config.ELEVENLABS_API_KEY)
            except ImportError:
                print("[Speaker] elevenlabs not installed. Falling back to edge-tts.")
                self.engine = "edge-tts"
            except Exception as e:
                print(f"[Speaker] ElevenLabs init error: {e}. Falling back to edge-tts.")
                self.engine = "edge-tts"
        
        if self.engine == "edge-tts":
            try:
                import edge_tts
            except ImportError:
                print("[Speaker] edge-tts not installed. Falling back to macOS say.")
                self.engine = "macos"

    def speak(self, text: str, block: bool = True) -> None:
        """
        Speak the given text using the configured TTS engine.
        
        Args:
            text: The text to speak.
            block: If True, waits for speech to finish before returning.
        """
        if not text or not text.strip():
            return

        text = text.strip()
        
        # Check cache first
        cache_key = f"{self.engine}:{text}"
        if cache_key in self._phrase_cache:
            cached_path = self._phrase_cache[cache_key]
            if os.path.exists(cached_path):
                self.player.play_file(cached_path, block=block)
                return

        try:
            if self.engine == "elevenlabs":
                self._speak_elevenlabs(text, block)
            elif self.engine == "edge-tts":
                self._speak_edge_tts(text, block)
            else:
                self._speak_macos(text, block)
        except Exception as e:
            print(f"[Speaker] TTS error with {self.engine}: {e}")
            # Fallback chain
            if self.engine == "elevenlabs":
                print("[Speaker] Falling back to edge-tts...")
                try:
                    self._speak_edge_tts(text, block)
                    return
                except Exception:
                    pass
            # Last resort
            print("[Speaker] Falling back to macOS say...")
            self._speak_macos(text, block)

    def _speak_elevenlabs(self, text: str, block: bool = True) -> None:
        """Generate speech using ElevenLabs API."""
        from elevenlabs import save as eleven_save

        audio = self.eleven_client.generate(
            text=text,
            voice=config.ELEVENLABS_VOICE,
            model=config.ELEVENLABS_MODEL,
            voice_settings={
                "stability": config.ELEVENLABS_STABILITY,
                "similarity_boost": config.ELEVENLABS_SIMILARITY_BOOST,
                "style": config.ELEVENLABS_STYLE,
                "use_speaker_boost": True
            }
        )
        
        # Save to temp file
        output_path = get_temp_audio_path(prefix="tts_eleven_", suffix=".mp3")
        eleven_save(audio, output_path)
        
        # Cache short phrases
        if len(text) < 100:
            self._phrase_cache[f"elevenlabs:{text}"] = output_path
        
        self.player.play_file(output_path, block=block)

    def _speak_edge_tts(self, text: str, block: bool = True) -> None:
        """Generate speech using Microsoft Edge TTS (free)."""
        import edge_tts

        output_path = get_temp_audio_path(prefix="tts_edge_", suffix=".mp3")

        async def _generate():
            communicate = edge_tts.Communicate(
                text=text,
                voice=config.EDGE_TTS_VOICE,
                pitch=config.EDGE_TTS_PITCH,
                rate=config.EDGE_TTS_RATE
            )
            await communicate.save(output_path)

        # Run async edge-tts in sync context
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    pool.submit(asyncio.run, _generate()).result()
            else:
                loop.run_until_complete(_generate())
        except RuntimeError:
            asyncio.run(_generate())
        
        # Cache short phrases
        if len(text) < 100:
            self._phrase_cache[f"edge-tts:{text}"] = output_path
        
        self.player.play_file(output_path, block=block)

    def _speak_macos(self, text: str, block: bool = True) -> None:
        """Generate speech using macOS built-in say command."""
        safe_text = text.replace('"', '\\"').replace("'", "'\\''")
        
        cmd = [
            "say",
            "-v", config.MACOS_VOICE,
            "-r", str(config.MACOS_VOICE_RATE),
            safe_text
        ]
        
        if block:
            subprocess.run(cmd, capture_output=True)
        else:
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def stop(self) -> None:
        """Stop any currently playing speech."""
        self.player.stop_playback()
        try:
            subprocess.run(["pkill", "-f", "say"], capture_output=True)
        except Exception:
            pass

    def get_engine_info(self) -> str:
        """Return info about the active TTS engine."""
        engine_names = {
            "elevenlabs": f"ElevenLabs ({config.ELEVENLABS_VOICE})",
            "edge-tts": f"Edge TTS ({config.EDGE_TTS_VOICE}, pitch={config.EDGE_TTS_PITCH})",
            "macos": f"macOS say ({config.MACOS_VOICE})"
        }
        return engine_names.get(self.engine, self.engine)

    def clear_cache(self) -> None:
        """Clear the phrase cache."""
        self._phrase_cache.clear()
