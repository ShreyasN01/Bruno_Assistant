"""
Bruno AI Assistant — Audio Utilities
Handles audio recording, playback, and voice activity detection.
"""

import os
import wave
import tempfile
import subprocess
import numpy as np
import sounddevice as sd
from typing import Optional

import config


class AudioRecorder:
    """Records audio from the microphone with voice activity detection."""

    def __init__(self):
        self.sample_rate = config.SAMPLE_RATE
        self.channels = config.CHANNELS
        self.silence_threshold = config.SILENCE_THRESHOLD
        self.silence_duration = config.SILENCE_DURATION
        self.max_duration = config.MAX_LISTEN_DURATION
        self.min_duration = config.MIN_LISTEN_DURATION

    def record_until_silence(self, timeout: Optional[float] = None) -> Optional[np.ndarray]:
        """
        Record audio from the microphone until silence is detected.
        
        Uses energy-based voice activity detection: records while the user
        is speaking, and stops after `silence_duration` seconds of silence.
        
        Args:
            timeout: Maximum recording time in seconds. Defaults to config.MAX_LISTEN_DURATION.
            
        Returns:
            numpy array of recorded audio, or None if nothing was recorded.
        """
        if timeout is None:
            timeout = self.max_duration

        chunk_duration = 0.1  # 100ms chunks for VAD
        chunk_samples = int(self.sample_rate * chunk_duration)
        
        frames = []
        silence_chunks = 0
        max_silence_chunks = int(self.silence_duration / chunk_duration)
        max_total_chunks = int(timeout / chunk_duration)
        speech_detected = False
        total_chunks = 0

        try:
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype='float32',
                blocksize=chunk_samples
            ) as stream:
                while total_chunks < max_total_chunks:
                    audio_chunk, overflowed = stream.read(chunk_samples)
                    frames.append(audio_chunk.copy())
                    total_chunks += 1

                    # Calculate RMS energy of the chunk
                    rms = np.sqrt(np.mean(audio_chunk ** 2)) * 32768  # Scale to 16-bit range
                    
                    if rms > self.silence_threshold:
                        speech_detected = True
                        silence_chunks = 0
                    else:
                        silence_chunks += 1

                    # Stop if we've had enough silence after speech
                    if speech_detected and silence_chunks >= max_silence_chunks:
                        break

        except Exception as e:
            print(f"[Audio] Recording error: {e}")
            return None

        if not speech_detected or len(frames) < int(self.min_duration / chunk_duration):
            return None

        # Concatenate all frames
        audio = np.concatenate(frames, axis=0).flatten()
        return audio

    def record_fixed_duration(self, duration: float = 5.0) -> Optional[np.ndarray]:
        """
        Record audio for a fixed duration.
        
        Args:
            duration: Recording duration in seconds.
            
        Returns:
            numpy array of recorded audio.
        """
        try:
            samples = int(self.sample_rate * duration)
            audio = sd.rec(
                samples,
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype='float32'
            )
            sd.wait()
            return audio.flatten()
        except Exception as e:
            print(f"[Audio] Recording error: {e}")
            return None


class AudioPlayer:
    """Plays audio files using macOS native tools."""

    @staticmethod
    def play_file(filepath: str, block: bool = True) -> None:
        """
        Play an audio file using macOS afplay.
        
        Args:
            filepath: Path to the audio file to play.
            block: If True, waits for playback to finish.
        """
        if not os.path.exists(filepath):
            return
        
        try:
            cmd = ["afplay", filepath]
            if block:
                subprocess.run(cmd, capture_output=True)
            else:
                subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"[Audio] Playback error: {e}")

    @staticmethod
    def stop_playback() -> None:
        """Stop any currently playing audio."""
        try:
            subprocess.run(["pkill", "-f", "afplay"], capture_output=True)
        except Exception:
            pass


def save_audio_to_wav(audio: np.ndarray, filepath: str, sample_rate: int = None) -> str:
    """
    Save a numpy audio array to a WAV file.
    
    Args:
        audio: numpy array of audio samples (float32, -1.0 to 1.0).
        filepath: Output file path.
        sample_rate: Sample rate in Hz.
        
    Returns:
        Path to the saved WAV file.
    """
    if sample_rate is None:
        sample_rate = config.SAMPLE_RATE

    # Convert float32 to int16
    audio_int16 = (audio * 32767).astype(np.int16)
    
    with wave.open(filepath, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(audio_int16.tobytes())
    
    return filepath


def get_temp_audio_path(prefix: str = "bruno_", suffix: str = ".wav") -> str:
    """Get a temporary file path in Bruno's cache directory for audio files."""
    os.makedirs(config.TEMP_AUDIO_DIR, exist_ok=True)
    fd, path = tempfile.mkstemp(prefix=prefix, suffix=suffix, dir=config.TEMP_AUDIO_DIR)
    os.close(fd)
    return path


def cleanup_temp_audio() -> None:
    """Remove old temporary audio files."""
    if not os.path.exists(config.TEMP_AUDIO_DIR):
        return
    
    for f in os.listdir(config.TEMP_AUDIO_DIR):
        filepath = os.path.join(config.TEMP_AUDIO_DIR, f)
        try:
            if os.path.isfile(filepath):
                os.unlink(filepath)
        except Exception:
            pass


def generate_activation_sound() -> str:
    """
    Generate a subtle activation 'ding' sound programmatically.
    
    Returns:
        Path to the generated WAV file.
    """
    filepath = os.path.join(config.SOUNDS_DIR, "activate.wav")
    if os.path.exists(filepath):
        return filepath

    # Generate a pleasant two-tone chime
    duration = 0.3  # seconds
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), dtype=np.float32)
    
    # Two frequencies for a pleasant ding
    freq1 = 880   # A5
    freq2 = 1320  # E6
    
    # Generate tones with envelope
    envelope = np.exp(-t * 8)  # Exponential decay
    tone = (0.4 * np.sin(2 * np.pi * freq1 * t) + 
            0.3 * np.sin(2 * np.pi * freq2 * t)) * envelope
    
    # Normalize
    tone = tone / np.max(np.abs(tone)) * 0.7
    
    save_audio_to_wav(tone, filepath, sample_rate)
    return filepath


def generate_deactivation_sound() -> str:
    """
    Generate a subtle deactivation sound programmatically.
    
    Returns:
        Path to the generated WAV file.
    """
    filepath = os.path.join(config.SOUNDS_DIR, "deactivate.wav")
    if os.path.exists(filepath):
        return filepath

    # Generate a descending tone
    duration = 0.2
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), dtype=np.float32)
    
    # Descending frequency
    freq = 880 - 400 * t / duration
    envelope = np.exp(-t * 6)
    tone = 0.4 * np.sin(2 * np.pi * freq * t) * envelope
    
    tone = tone / np.max(np.abs(tone)) * 0.5
    
    save_audio_to_wav(tone, filepath, sample_rate)
    return filepath
