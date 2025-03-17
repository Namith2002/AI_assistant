from flask import Flask, render_template, request, jsonify, send_file
from assistant import AIAssistant
import threading
import logging
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
assistant = AIAssistant()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    try:
        data = request.json
        user_input = data.get('input')
        
        if not user_input:
            return jsonify({'error': 'No input provided'}), 400
        
        response = assistant.get_ai_response(user_input)
        if response:
            # Generate audio response
            assistant.engine.save_to_file(response, 'temp_response.mp3')
            assistant.engine.runAndWait()
            
            return jsonify({
                'response': response,
                'audio_url': '/get_audio'
            })
        
        return jsonify({'error': 'No response generated'}), 500
        
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/get_audio')
def get_audio():
    try:
        return send_file('temp_response.mp3', mimetype='audio/mpeg')
    except Exception as e:
        logger.error(f"Error sending audio: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(HTTPException)
def handle_exception(e):
    return jsonify({'error': str(e)}), e.code

if __name__ == '__main__':
    app.run(debug=True)