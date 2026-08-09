# Bruno — AI Voice Assistant 🎩

*“By order of the Peaky Blinders.”*

Bruno is a fully functional, modular macOS personal AI voice assistant with the personality and voice of Thomas Shelby. He listens for your wake word, understands natural language, executes real macOS system actions, and responds with a deep, commanding voice.

## 🚀 Features

- **Voice Activated:** Wake word detection (e.g., "Hey Bruno") or push-to-talk (`--no-wake`).
- **Natural Conversations:** Powered by Groq's blazing fast Llama 3 models for instant reasoning.
- **Mac Control (26+ Actions):** 
  - 🖥️ **Apps:** Open, close, or focus any app (with fuzzy matching aliases).
  - 💬 **Messaging:** Send iMessages directly to contacts.
  - 🔍 **Web:** Search Google and open URLs.
  - 🎵 **Media:** Control Spotify and Apple Music (play, pause, next, search).
  - ⚙️ **System:** Adjust volume, brightness, dark mode, Wi-Fi, battery, and lock screen.
  - 📅 **Productivity:** Check calendar events, read reminders, and create new ones.
  - 📂 **Files:** Search files via Spotlight and open them.
- **Multiple Voice Engines:** Supports premium ElevenLabs, free Edge TTS, and offline macOS say.
- **Rich Terminal UI:** A beautiful, themed command-line interface.

## 🛠️ Architecture

Bruno is built with a highly decoupled, modular pipeline:

1. **Microphone (core/audio.py):** Captures voice using PyAudio.
2. **Wake Word (core/wake_word.py):** Uses Picovoice Porcupine or a continuous speech recognition fallback.
3. **Speech-to-Text (core/listener.py):** Uses `faster-whisper` running locally (no API cost).
4. **AI Brain (core/brain.py):** Uses OpenAI-compatible function calling (via Groq/NVIDIA APIs) to determine intent.
5. **Command Router (core/router.py):** Maps AI tool calls to Python functions.
6. **Action Handlers (actions/*):** Executes AppleScript/Subprocess commands on macOS.
7. **Text-to-Speech (core/speaker.py):** Speaks the result back using Edge TTS or ElevenLabs.

## ⚙️ Setup & Installation

### 1. Prerequisites
- macOS (for AppleScript integrations).
- Python 3.10+
- Homebrew (for installing system audio libraries).

### 2. Install
Run the automated setup script to install all Homebrew dependencies and Python packages:
```bash
chmod +x setup.sh
./setup.sh
```

### 3. API Keys
Copy the example environment file and add your keys:
```bash
cp .env.example .env
nano .env
```
*Note: The primary brain requires an OpenAI-compatible API key (like Groq's free Llama 3.3 endpoint).*

## 🏃‍♂️ Usage

Activate the virtual environment:
```bash
source venv/bin/activate
```

Run Bruno:
```bash
# Push-to-talk mode (Best for testing — press Enter to speak)
python bruno.py --no-wake

# Wake-word mode (Say "Hey Bruno" out loud)
python bruno.py
```

## 🧠 Customization

You can customize Bruno's personality, TTS speed, STT models, and more by editing `config.py`. 
To change his voice to a premium ElevenLabs clone, add an `ELEVENLABS_API_KEY` to your `.env` file.
