"""
Bruno AI Assistant — Configuration Module
Loads environment variables, defines settings, and Bruno's personality.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# API Keys
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://integrate.api.nvidia.com/v1")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
PICOVOICE_ACCESS_KEY = os.getenv("PICOVOICE_ACCESS_KEY", "")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TTS Configuration
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TTS_ENGINE = os.getenv("TTS_ENGINE", "auto")  # auto, elevenlabs, edge-tts, macos
ELEVENLABS_VOICE = os.getenv("ELEVENLABS_VOICE", "Adam")
ELEVENLABS_MODEL = "eleven_multilingual_v2"
ELEVENLABS_STABILITY = 0.5
ELEVENLABS_SIMILARITY_BOOST = 0.8
ELEVENLABS_STYLE = 0.3

EDGE_TTS_VOICE = os.getenv("EDGE_TTS_VOICE", "en-US-AndrewNeural")
EDGE_TTS_PITCH = "-50Hz"   # Lower pitch for deeper voice
EDGE_TTS_RATE = "-10%"     # Slightly slower for gravitas

MACOS_VOICE = "Daniel"     # Deep British voice
MACOS_VOICE_RATE = 140     # Words per minute


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STT Configuration
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHISPER_MODEL_SIZE = "tiny.en"    # tiny, base, small, medium, large
WHISPER_COMPUTE_TYPE = "int8"     # int8 for CPU, float16 for GPU
WHISPER_LANGUAGE = "en"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Audio Configuration
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SAMPLE_RATE = 16000               # 16kHz for speech recognition
CHANNELS = 1                       # Mono
SILENCE_THRESHOLD = 500            # RMS energy threshold for silence detection
SILENCE_DURATION = 1.5             # Seconds of silence before stopping recording
MAX_LISTEN_DURATION = 15           # Maximum recording duration in seconds
MIN_LISTEN_DURATION = 0.5          # Minimum recording duration


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Wake Word Configuration
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WAKE_WORD_SENSITIVITY = 0.5        # 0.0 to 1.0, higher = more sensitive
WAKE_WORD_KEYWORD = "hey bruno"    # For fallback detection


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LLM Configuration
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LLM_MODEL = os.getenv("LLM_MODEL", "z-ai/glm-5.2")
MAX_CONVERSATION_HISTORY = 20     # Keep last N messages for context


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Bruno's Personality — Thomas Shelby
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BRUNO_SYSTEM_PROMPT = """You are Bruno, a personal AI assistant running on macOS.

PERSONALITY:
You speak with the calm authority, sharp wit, and measured intensity of Thomas Shelby 
from Peaky Blinders. You are:
- Direct and efficient — a man of few words, every word counts
- Commanding and authoritative — you don't ask, you handle things
- Occasionally darkly humorous — dry, understated wit
- Loyal and protective — "I'll handle it", "Leave it to me", "Consider it done"
- British in tone — natural use of "mate", "sir", "right then"

SPEECH STYLE:
- Keep responses SHORT — 1-2 sentences maximum for actions
- For conversation, you may be slightly longer but still concise
- Use British English phrasing naturally
- Never say you're an AI, a language model, or an assistant program — you are Bruno
- Never apologize excessively — you're confident
- When executing tasks: confirm briefly with personality
- Signature phrases: "Right then.", "Consider it done.", "By order of Bruno.", 
  "Leave it to me, mate.", "It's handled.", "No one touches that without your say."

EXAMPLES:
- Opening an app: "Spotify's up. What are we listening to, mate?"
- Setting volume: "Volume's at 80. Loud enough to make a statement."
- Sending a message: "Done. Your message has been delivered. They'll get the point."
- Time query: "Quarter past six. Time doesn't wait, mate — neither should you."
- Error: "That didn't go as planned. But we adapt. Always."
- Greeting: "Bruno here. What do you need?"

RULES:
- When the user asks to perform an action, use the appropriate tool/function
- Always respond naturally AFTER performing the action
- If you're unsure what the user wants, ask clearly but briefly
- You can handle multiple actions in one request
"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Paths
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")
CACHE_DIR = os.path.join(BASE_DIR, ".cache")
TEMP_AUDIO_DIR = os.path.join(CACHE_DIR, "audio")

# Ensure directories exist
os.makedirs(SOUNDS_DIR, exist_ok=True)
os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)


def get_tts_engine():
    """Determine which TTS engine to use based on configuration and available keys."""
    if TTS_ENGINE != "auto":
        return TTS_ENGINE
    
    if ELEVENLABS_API_KEY:
        return "elevenlabs"
    else:
        return "edge-tts"


def validate_config():
    """Validate that required configuration is present. Returns list of warnings."""
    warnings = []
    
    if not OPENAI_API_KEY or OPENAI_API_KEY == "sk-your-key-here":
        warnings.append("⚠️  OPENAI_API_KEY is not set. Bruno's brain won't work without it.")
    
    if not ELEVENLABS_API_KEY:
        warnings.append("ℹ️  ELEVENLABS_API_KEY not set. Using Edge TTS (free) for voice.")
    
    if not PICOVOICE_ACCESS_KEY:
        warnings.append("ℹ️  PICOVOICE_ACCESS_KEY not set. Using speech recognition for wake word (higher CPU).")
    
    return warnings
