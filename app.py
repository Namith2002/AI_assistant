from flask import Flask, render_template, request, jsonify
from assistant import AIAssistant
import threading

app = Flask(__name__)
assistant = AIAssistant()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    user_input = data.get('input')
    
    if user_input:
        response = assistant.get_ai_response(user_input)
        return jsonify({'response': response})
    
    return jsonify({'error': 'No input provided'})

if __name__ == '__main__':
    app.run(debug=True)