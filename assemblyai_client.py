import websocket
import json
import threading
import time
from typing import Callable
from urllib.parse import urlencode

class AssemblyAIClient:
    def __init__(self, api_key: str, sample_rate: int = 16000):
        self.api_key = api_key
        self.sample_rate = sample_rate
        self.ws = None
        self.is_connected = False
        self.on_transcript = None
        self.session_id = None
        
        # Connection parameters for new API
        connection_params = {
            "sample_rate": sample_rate,
            "format_turns": False  # We want partial transcripts
        }
        
        # New API endpoint
        api_endpoint_base = "wss://streaming.assemblyai.com/v3/ws"
        self.url = f"{api_endpoint_base}?{urlencode(connection_params)}"
        
        print(f"DEBUG: AssemblyAI URL: {self.url}")
        
    def set_transcript_callback(self, callback: Callable[[dict], None]):
        """Set callback function for transcript events"""
        self.on_transcript = callback
        
    def connect(self):
        """Connect to AssemblyAI WebSocket"""
        try:
            print(f"DEBUG: Connecting to {self.url}")
            
            self.ws = websocket.WebSocketApp(
                self.url,
                header={"Authorization": self.api_key},
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )
            
            # Start WebSocket in separate thread
            ws_thread = threading.Thread(target=self.ws.run_forever, daemon=True)
            ws_thread.start()
            
            # Wait for connection
            max_wait = 10
            start_time = time.time()
            while not self.is_connected and (time.time() - start_time) < max_wait:
                time.sleep(0.1)
                
            if not self.is_connected:
                raise Exception("Failed to connect to AssemblyAI within timeout")
                
            print("Connected to AssemblyAI streaming service")
            
        except Exception as e:
            print(f"Error connecting to AssemblyAI: {e}")
            raise
            
    def _on_open(self, ws):
        """WebSocket connection opened"""
        print("DEBUG: WebSocket connection opened")
        self.is_connected = True
        
    def _on_message(self, ws, message):
        """Handle incoming WebSocket message"""
        try:
            print(f"DEBUG: Raw message: {message}")
            data = json.loads(message)
            msg_type = data.get('type')
            
            print(f"DEBUG: Message type: {msg_type}")
            
            if msg_type == "Begin":
                self.session_id = data.get('id')
                expires_at = data.get('expires_at')
                print(f"AssemblyAI session started: {self.session_id}, expires: {expires_at}")
                
            elif msg_type == "Turn":
                # This is a transcript
                transcript = data.get('transcript', '').strip()
                formatted = data.get('turn_is_formatted', False)
                end_of_turn = data.get('end_of_turn', False)
                
                if transcript and self.on_transcript:
                    # Convert to our expected format
                    transcript_data = {
                        'text': transcript,
                        'message_type': 'FinalTranscript' if (formatted or end_of_turn) else 'PartialTranscript'
                    }
                    print(f"DEBUG: Calling transcript callback with: {transcript_data}")
                    self.on_transcript(transcript_data)
                    
            elif msg_type == "Termination":
                audio_duration = data.get('audio_duration_seconds', 0)
                session_duration = data.get('session_duration_seconds', 0)
                print(f"Session terminated: Audio={audio_duration}s, Session={session_duration}s")
                
        except json.JSONDecodeError as e:
            print(f"Error parsing AssemblyAI message: {e}")
        except Exception as e:
            print(f"Error handling AssemblyAI message: {e}")
            
    def _on_error(self, ws, error):
        """WebSocket error handler"""
        print(f"AssemblyAI WebSocket error: {error}")
        
    def _on_close(self, ws, close_status_code, close_msg):
        """WebSocket connection closed"""
        self.is_connected = False
        print(f"AssemblyAI connection closed: Status={close_status_code}, Msg={close_msg}")
        
    def send_audio(self, audio_chunk: bytes):
        """Send audio chunk to AssemblyAI"""
        if not self.is_connected or not self.ws:
            return
            
        try:
            # Send audio as binary data (new API format)
            self.ws.send(audio_chunk, websocket.ABNF.OPCODE_BINARY)
            
        except Exception as e:
            print(f"Error sending audio to AssemblyAI: {e}")
            
    def close(self):
        """Close WebSocket connection"""
        if self.ws:
            try:
                # Send termination message
                terminate_message = {"type": "Terminate"}
                self.ws.send(json.dumps(terminate_message))
                time.sleep(0.1)  # Give time for message to send
            except:
                pass
            self.ws.close()
        self.is_connected = False