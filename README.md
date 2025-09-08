# DAMN: Dynamic Audio Monitoring and Narration

A Python application that provides real-time live subtitles in English for whatever you hear through your USB-C earphones' microphone, with optional OLED display support for Raspberry Pi.

## Features

- **Real-time Audio Capture**: Uses PyAudio to capture audio from USB-C earphones with microphone
- **Streaming Speech-to-Text**: AssemblyAI Realtime API for live transcription
- **AI Translation**: Gemini 1.5 Flash API for natural English translation
- **Rich Terminal Display**: Beautiful formatted output using Rich library with dual panels
- **OLED/I2C Display Support**: Real-time subtitles and translations on SSD1306 OLED (I2C)

## Requirements

### Hardware
- Raspberry Pi 4 (4GB RAM recommended)
- USB-C earphones with built-in microphone
- SSD1306 OLED display (I2C, 128x64 recommended)
- Internet connection

### Software
- Raspberry Pi OS (64-bit, Debian based)
- Python 3.11+
- System dependencies: `portaudio19-dev`, `i2c-tools`, `python3-pil`, `python3-dev`, `libffi-dev`, `libjpeg-dev`, `zlib1g-dev`

## Installation

1. **Install system dependencies**:
   ```bash
   sudo apt update
   sudo apt install -y portaudio19-dev i2c-tools python3-pil python3-dev libffi-dev libjpeg-dev zlib1g-dev
   ```

2. **Clone/download this project** to your Raspberry Pi

3. **Set up API keys**:
   - Copy `.env.example` to `.env` (or create `.env`)
   - Add your API keys:
     ```
     ASSEMBLYAI_API_KEY=your_assemblyai_api_key_here
     GEMINI_API_KEY=your_gemini_api_key_here
     ```

4. **Run the setup script** (recommended):
   ```bash
   bash setup.sh
   ```
   This will create a virtual environment, install all Python dependencies, and launch the app.

   Or, to do it manually:
   ```bash
   python3 -m venv damn-env
   source damn-env/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   python main.py
   ```

## API Keys Setup

### AssemblyAI API Key
1. Sign up at [AssemblyAI](https://www.assemblyai.com/)
2. Go to your dashboard and copy your API key
3. Add it to your `.env` file

### Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file

## Usage

1. **Run the application**:
   ```bash
   bash setup.sh
   ```
   or (if already set up):
   ```bash
   source damn-env/bin/activate
   python main.py
   ```

2. **Start speaking**: The application will display:
   - **Original panel**: Shows the transcribed text in the detected language
   - **English Translation panel**: Shows the natural English translation
   - **OLED Display**: Shows real-time partial and final subtitles/translation (if SSD1306 is connected)
   - **Status indicators**: Shows partial transcripts (⏳) and connection status

3. **Stop**: Press `Ctrl+C` to stop the application

## How It Works

1. **Audio Capture**: Captures audio from your USB-C earphones at 48kHz, mono, 16-bit
2. **Streaming STT**: Sends audio in real-time to AssemblyAI WebSocket endpoint
3. **Transcription**: Receives partial and final transcripts from AssemblyAI
4. **Translation**: For each final transcript, calls Gemini API to translate to natural English
5. **Display**: Shows both original and English text in formatted terminal panels and on OLED

## Troubleshooting

### Audio Device Issues
- Run the app once to see available devices
- Make sure your USB-C earphones are properly connected
- Check `lsusb` to verify device recognition

### API Connection Issues
- Verify your API keys are correct in `.env`
- Check internet connection
- Ensure firewall allows WebSocket connections

### OLED/I2C Issues
- Ensure I2C is enabled (`sudo raspi-config` > Interface Options > I2C)
- Use `sudo i2cdetect -y 1` to verify your OLED is detected (should show address, e.g., 3c)
- Check wiring (SCL/SDA)

### Performance Issues
- Close other applications to free up RAM
- Ensure good internet connection for real-time performance
- OLED display is now non-blocking and real-time

## Project Structure

- `main.py` - Main application entry point
- `assemblyai_client.py` - WebSocket client for AssemblyAI streaming API
- `translation_service.py` - Gemini API integration for translation
- `displayOLED.py` - OLED display logic (SSD1306, I2C)
- `requirements.txt` - Python dependencies
- `setup.sh` - Setup and launch script
- `.env.example` - Environment variables template

## Future Enhancements

- Voice activity detection
- Multiple language support
- Offline mode with local models
- Audio file processing mode
- More display options (e.g., LCD, e-ink)

---

**Project Name:** DAMN (Dynamic Audio Monitoring and Narration)