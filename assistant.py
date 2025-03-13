import speech_recognition as sr
import pyttsx3
import openai
import json
import os
from dotenv import load_dotenv

class AIAssistant:
    def __init__(self):
        # Initialize OpenAI API
        load_dotenv()
        openai.api_key = os.getenv('OPENAI_API_KEY')
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        
        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        
    def listen(self):
        with sr.Microphone() as source:
            print("Listening...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = self.recognizer.listen(source)
            
        try:
            text = self.recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return None
            
    def get_ai_response(self, prompt):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error getting AI response: {e}")
            return None
            
    def speak(self, text):
        print(f"Assistant: {text}")
        self.engine.say(text)
        self.engine.runAndWait()
        
    def run(self):
        self.speak("Hello! How can I help you today?")
        
        while True:
            user_input = self.listen()
            
            if user_input:
                if "goodbye" in user_input.lower():
                    self.speak("Goodbye! Have a great day!")
                    break
                    
                response = self.get_ai_response(user_input)
                if response:
                    self.speak(response)

if __name__ == "__main__":
    assistant = AIAssistant()
    assistant.run()