import google.generativeai as genai
from typing import Optional
import time

class TranslationService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        
        # Initialize Gemini model
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests
        
    def translate_to_english(self, text: str, source_language: Optional[str] = None) -> str:
        """Translate text to natural English using Gemini"""
        if not text or not text.strip():
            return ""
            
        # Rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        
        try:
            # Construct prompt for natural translation
            if source_language:
                prompt = f"""Translate this {source_language} text to natural, fluent English. 
                Keep the meaning intact but make it sound natural to English speakers:

                "{text}"
                
                Respond only with the English translation, no explanations."""
            else:
                prompt = f"""If this text is not in English, translate it to natural, fluent English. 
                If it's already in English, improve it to sound more natural and fluent.
                Keep the meaning intact:

                "{text}"
                
                Respond only with the improved/translated English text, no explanations."""
            
            response = self.model.generate_content(prompt)
            self.last_request_time = time.time()
            
            if response and response.text:
                return response.text.strip()
            else:
                return text  # Return original if no response
                
        except Exception as e:
            print(f"Translation error: {e}")
            return text  # Return original text if translation fails
    
    def detect_and_translate(self, text: str) -> tuple[str, str]:
        """Detect language and translate to English"""
        if not text or not text.strip():
            return "", ""
            
        try:
            # First, detect the language
            detect_prompt = f"""What language is this text in? Respond with just the language name in English:

            "{text}"
            
            Respond only with the language name (e.g., "Spanish", "French", "English", etc.)"""
            
            detect_response = self.model.generate_content(detect_prompt)
            detected_language = detect_response.text.strip() if detect_response.text else "Unknown"
            
            # Then translate if not English
            if detected_language.lower() != "english":
                translated = self.translate_to_english(text, detected_language)
                return detected_language, translated
            else:
                return "English", text
                
        except Exception as e:
            print(f"Language detection error: {e}")
            # Fallback to direct translation
            translated = self.translate_to_english(text)
            return "Unknown", translated