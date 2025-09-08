#!/usr/bin/env python3

import os
import sys
import threading
import time
from dotenv import load_dotenv
import pyaudio
import json

from assemblyai_client import AssemblyAIClient
from translation_service import TranslationService

class SimpleSubtitleSystem:
    def __init__(self):
        load_dotenv()
        
        self.assemblyai_key = os.getenv('ASSEMBLYAI_API_KEY')
        self.gemini_key = os.getenv('GEMINI_API_KEY')
        
        if not self.assemblyai_key or not self.gemini_key:
            print("Error: Missing API keys in .env file")
            sys.exit(1)
        
        self.assemblyai_client = AssemblyAIClient(self.assemblyai_key, sample_rate=48000)
        self.translation_service = TranslationService(self.gemini_key)
        
        self.running = False
        self.audio = None
        self.stream = None
        
    def on_transcript(self, transcript_data):
        """Handle transcript from AssemblyAI"""
        text = transcript_data.get('text', '').strip()
        is_partial = transcript_data.get('message_type') == 'PartialTranscript'
        
        if not text:
            return
        
        timestamp = time.strftime("%H:%M:%S")
        status = "⏳" if is_partial else "✅"
        
        print(f"\n[{timestamp}] {status}")
        print(f"Original: {text}")
        
        # For final transcripts, get translation
        if not is_partial:
            try:
                language, english_translation = self.translation_service.detect_and_translate(text)
                print(f"Language: {language}")
                if english_translation != text:
                    print(f"English: {english_translation}")
                else:
                    print(f"English: {english_translation} (no translation needed)")
                print("-" * 60)
            except Exception as e:
                print(f"Translation error: {e}")
                print("-" * 60)
    
    def audio_thread(self):
        """Audio capture and streaming thread"""
        try:
            while self.running:
                data = self.stream.read(2400, exception_on_overflow=False)  # Match frames_per_buffer
                self.assemblyai_client.send_audio(data)
        except Exception as e:
            print(f"Audio thread error: {e}")
    
    def start(self):
        """Start the system"""
        try:
            print("="*60)
            print("🎧 SIMPLE REAL-TIME SUBTITLES")
            print("="*60)
            
            # Set up AssemblyAI callback
            self.assemblyai_client.set_transcript_callback(self.on_transcript)
            
            # Connect to AssemblyAI
            print("Connecting to AssemblyAI...")
            self.assemblyai_client.connect()
            print("✅ Connected to AssemblyAI")
            
            # Set up audio
            print("Setting up audio...")
            self.audio = pyaudio.PyAudio()
            self.stream = self.audio.open(
                input=True,
                input_device_index=1,  # EarPods
                channels=1,
                format=pyaudio.paInt16,
                rate=48000,
                frames_per_buffer=2400  # ~50ms at 48kHz (2400/48000 = 0.05s)
            )
            print("✅ Audio ready")
            
            # Start audio thread
            self.running = True
            audio_thread = threading.Thread(target=self.audio_thread, daemon=True)
            audio_thread.start()
            
            print("🎤 Ready! Start speaking...")
            print("Press Ctrl+C to stop")
            print("-" * 60)
            
            # Keep running
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nStopping...")
                
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the system"""
        self.running = False
        
        if self.stream:
            self.stream.close()
        if self.audio:
            self.audio.terminate()
        if self.assemblyai_client:
            self.assemblyai_client.close()
        
        print("System stopped")

def main():
    system = SimpleSubtitleSystem()
    system.start()

if __name__ == "__main__":
    main()