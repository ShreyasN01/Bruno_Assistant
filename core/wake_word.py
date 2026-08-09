"""
Bruno AI Assistant — Wake Word Detection
Listens for "Hey Bruno" to activate the assistant.

Supports two modes:
1. Picovoice Porcupine — Lightweight, accurate, on-device (requires API key)
2. Continuous Speech Recognition — Fallback using faster-whisper (higher CPU)
"""

import os
import time
import numpy as np
from typing import Optional

import config


class WakeWordDetector:
    """
    Detects the wake word "Hey Bruno" from microphone audio.
    
    Uses Picovoice Porcupine if a key is configured, otherwise falls
    back to continuous speech recognition scanning for "bruno".
    """

    def __init__(self):
        self.use_porcupine = bool(config.PICOVOICE_ACCESS_KEY)
        self._porcupine = None
        self._recorder = None
        self._whisper_model = None
        
        if self.use_porcupine:
            self._init_porcupine()
        else:
            self._init_fallback()

    def _init_porcupine(self) -> None:
        """Initialize Picovoice Porcupine for wake word detection."""
        try:
            import pvporcupine
            from pvrecorder import PvRecorder
            
            # Check for custom wake word model
            custom_keyword_path = os.path.join(config.ASSETS_DIR, "hey_bruno_mac.ppn")
            
            if os.path.exists(custom_keyword_path):
                # Use custom "Hey Bruno" model
                self._porcupine = pvporcupine.create(
                    access_key=config.PICOVOICE_ACCESS_KEY,
                    keyword_paths=[custom_keyword_path],
                    sensitivities=[config.WAKE_WORD_SENSITIVITY]
                )
            else:
                # Use built-in "computer" as placeholder
                # User should generate custom model at console.picovoice.ai
                print("[WakeWord] Custom 'Hey Bruno' model not found at assets/hey_bruno_mac.ppn")
                print("[WakeWord] Using built-in 'computer' keyword. Generate custom model at console.picovoice.ai")
                self._porcupine = pvporcupine.create(
                    access_key=config.PICOVOICE_ACCESS_KEY,
                    keywords=["computer"],
                    sensitivities=[config.WAKE_WORD_SENSITIVITY]
                )
            
            self._recorder = PvRecorder(
                device_index=-1,
                frame_length=self._porcupine.frame_length
            )
            
            print("[WakeWord] Porcupine initialized successfully.")
            
        except ImportError:
            print("[WakeWord] pvporcupine not installed. Falling back to speech recognition.")
            self.use_porcupine = False
            self._init_fallback()
        except Exception as e:
            print(f"[WakeWord] Porcupine error: {e}. Falling back to speech recognition.")
            self.use_porcupine = False
            self._init_fallback()

    def _init_fallback(self) -> None:
        """Initialize fallback wake word detection using continuous STT."""
        try:
            from faster_whisper import WhisperModel
            print("[WakeWord] Using speech recognition fallback (scans for 'bruno' in speech).")
            print("[WakeWord] Loading Whisper 'tiny' model for wake word detection...")
            self._whisper_model = WhisperModel("tiny", device="cpu", compute_type="int8")
            print("[WakeWord] Whisper tiny model loaded for wake word detection.")
        except ImportError:
            print("[WakeWord] faster-whisper not installed. Wake word detection unavailable.")
            self._whisper_model = None

    def listen(self) -> bool:
        """
        Block until the wake word is detected.
        
        Returns:
            True when wake word is detected.
        """
        if self.use_porcupine:
            return self._listen_porcupine()
        else:
            return self._listen_fallback()

    def _listen_porcupine(self) -> bool:
        """Listen for wake word using Porcupine."""
        self._recorder.start()
        
        try:
            while True:
                audio_frame = self._recorder.read()
                keyword_index = self._porcupine.process(audio_frame)
                
                if keyword_index >= 0:
                    self._recorder.stop()
                    return True
        except KeyboardInterrupt:
            self._recorder.stop()
            raise

    def _listen_fallback(self) -> bool:
        """
        Listen for wake word using continuous speech recognition.
        
        Records 2-second chunks and scans for "bruno" in the transcription.
        Higher CPU usage than Porcupine but works without API key.
        """
        import sounddevice as sd
        
        chunk_duration = 2.0  # seconds per chunk
        chunk_samples = int(config.SAMPLE_RATE * chunk_duration)
        
        while True:
            try:
                # Record a short chunk
                audio = sd.rec(
                    chunk_samples,
                    samplerate=config.SAMPLE_RATE,
                    channels=1,
                    dtype='float32'
                )
                sd.wait()
                
                audio_flat = audio.flatten()
                
                # Check if there's any meaningful audio (skip silence)
                rms = np.sqrt(np.mean(audio_flat ** 2)) * 32768
                if rms < 200:  # Too quiet, skip transcription
                    continue
                
                # Transcribe the chunk
                if self._whisper_model is not None:
                    from core.audio import save_audio_to_wav, get_temp_audio_path
                    temp_path = get_temp_audio_path(prefix="wake_")
                    save_audio_to_wav(audio_flat, temp_path)
                    
                    try:
                        segments, _ = self._whisper_model.transcribe(
                            temp_path,
                            beam_size=1,
                            language="en",
                            vad_filter=True
                        )
                        
                        text = " ".join(s.text for s in segments).lower().strip()
                        
                        if "bruno" in text:
                            return True
                    finally:
                        try:
                            os.unlink(temp_path)
                        except OSError:
                            pass
                
            except KeyboardInterrupt:
                raise
            except Exception:
                time.sleep(0.5)

    def cleanup(self) -> None:
        """Release wake word detector resources."""
        if self._porcupine is not None:
            self._porcupine.delete()
            self._porcupine = None
        
        if self._recorder is not None:
            try:
                self._recorder.stop()
            except Exception:
                pass
            self._recorder = None

    def get_detector_info(self) -> str:
        """Return info about the active wake word detector."""
        if self.use_porcupine:
            return 'Picovoice Porcupine ("Hey Bruno")'
        else:
            return 'Speech Recognition (scanning for "Bruno")'
