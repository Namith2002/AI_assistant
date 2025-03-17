import speech_recognition as sr
import pyttsx3
import openai
import json
import os
import datetime
from dotenv import load_dotenv
from typing import Optional

class AIAssistant:
    def __init__(self):
        # Initialize OpenAI API
        load_dotenv()
        openai.api_key = os.getenv('OPENAI_API_KEY')
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        
        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()
        self.setup_voice()
        
        # Conversation history
        self.conversation_history = []
        
    def setup_voice(self):
        self.engine.setProperty('rate', 150)
        voices = self.engine.getProperty('voices')
        # Set default voice (index 0 for male, 1 for female)
        self.engine.setProperty('voice', voices[1].id)
        
    def listen(self) -> Optional[str]:
        with sr.Microphone() as source:
            print("\n🎤 Listening...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=5)
            
        try:
            text = self.recognizer.recognize_google(audio)
            print(f"🗣️ You said: {text}")
            return text
        except sr.UnknownValueError:
            print("❌ Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"❌ Could not request results; {e}")
            return None
            
    def get_ai_response(self, prompt: str) -> Optional[str]:
        try:
            # Add user message to history
            self.conversation_history.append({"role": "user", "content": prompt})
            
            messages = [
                {"role": "system", "content": "You are a helpful and friendly assistant."},
                *self.conversation_history[-5:]  # Keep last 5 messages for context
            ]
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=150
            )
            
            ai_response = response.choices[0].message.content
            # Add AI response to history
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            return ai_response
            
        except Exception as e:
            print(f"❌ Error getting AI response: {e}")
            return None
            
    def speak(self, text: str) -> None:
        # Display response in text format
        print("\n" + "="*50)
        print("🤖 Assistant Response:")
        print(text)
        print("="*50 + "\n")
        
        # Convert text to speech
        self.engine.say(text)
        self.engine.runAndWait()
        
    def save_conversation(self) -> None:
        if not self.conversation_history:
            return
            
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversation_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.conversation_history, f, ensure_ascii=False, indent=2)
        
    def run(self) -> None:
        try:
            self.speak("Hello! How can I help you today?")
            
            while True:
                user_input = self.listen()
                
                if user_input:
                    if "goodbye" in user_input.lower():
                        self.speak("Goodbye! Have a great day!")
                        self.save_conversation()
                        break
                        
                    response = self.get_ai_response(user_input)
                    if response:
                        self.speak(response)
                        
        except KeyboardInterrupt:
            print("\n\nExiting gracefully...")
            self.save_conversation()
            
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
            self.save_conversation()

if __name__ == "__main__":
    assistant = AIAssistant()
    assistant.run()