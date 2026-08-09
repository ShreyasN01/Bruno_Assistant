"""
Bruno AI Assistant — Speech-to-Text (Listener)
Transcribes spoken audio to text using faster-whisper.
"""

import os
import numpy as np
from typing import Optional

import config
from core.audio import AudioRecorder, save_audio_to_wav, get_temp_audio_path


class Listener:
    """
    Speech-to-Text engine using faster-whisper.
    
    Listens to the microphone, records until silence, and transcribes
    the audio to text using OpenAI's Whisper model running locally.
    """

    def __init__(self):
        self.model = None
        self.recorder = AudioRecorder()
        self._model_loaded = False
        self._load_model()

    def _load_model(self) -> None:
        """Lazy-load the Whisper model on first use."""
        if self._model_loaded:
            return
        
        try:
            from faster_whisper import WhisperModel
            
            print(f"[Listener] Loading Whisper '{config.WHISPER_MODEL_SIZE}' model...")
            self.model = WhisperModel(
                config.WHISPER_MODEL_SIZE,
                device="cpu",
                compute_type=config.WHISPER_COMPUTE_TYPE
            )
            self._model_loaded = True
            print("[Listener] Whisper model loaded.")
        except ImportError:
            print("[Listener] faster-whisper not installed. Install with: pip install faster-whisper")
            raise
        except Exception as e:
            print(f"[Listener] Error loading Whisper model: {e}")
            raise

    def listen(self, timeout: Optional[float] = None) -> Optional[str]:
        """
        Record audio from the microphone and transcribe it to text.
        
        Records until silence is detected (or timeout), then runs
        the Whisper model to transcribe the audio.
        
        Args:
            timeout: Maximum recording time in seconds.
            
        Returns:
            Transcribed text string, or None if nothing was heard.
        """
        self._load_model()

        # Record audio
        audio = self.recorder.record_until_silence(timeout=timeout)
        
        if audio is None or len(audio) == 0:
            return None

        # Save to temporary WAV file (Whisper needs a file)
        temp_path = get_temp_audio_path(prefix="stt_")
        try:
            save_audio_to_wav(audio, temp_path)
            
            # Transcribe
            text = self._transcribe(temp_path)
            return text
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except OSError:
                pass

    def transcribe_file(self, filepath: str) -> Optional[str]:
        """
        Transcribe an existing audio file to text.
        
        Args:
            filepath: Path to the audio file.
            
        Returns:
            Transcribed text string.
        """
        self._load_model()
        return self._transcribe(filepath)

    def _transcribe(self, filepath: str) -> Optional[str]:
        """
        Run Whisper transcription on an audio file.
        
        Args:
            filepath: Path to WAV file.
            
        Returns:
            Transcribed text, or None on failure.
        """
        try:
            segments, info = self.model.transcribe(
                filepath,
                beam_size=1,           # Faster, single beam
                language=config.WHISPER_LANGUAGE,
                vad_filter=True,       # Filter out non-speech
                vad_parameters=dict(
                    min_silence_duration_ms=500,
                    speech_pad_ms=200
                )
            )
            
            # Collect all segment texts
            text_parts = []
            for segment in segments:
                text_parts.append(segment.text.strip())
            
            text = " ".join(text_parts).strip()
            
            if not text:
                return None
            
            return text

        except Exception as e:
            print(f"[Listener] Transcription error: {e}")
            return None

    def get_model_info(self) -> str:
        """Return info about the loaded model."""
        return f"faster-whisper ({config.WHISPER_MODEL_SIZE}, {config.WHISPER_COMPUTE_TYPE})"
