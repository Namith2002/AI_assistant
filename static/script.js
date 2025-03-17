let mediaRecorder;
let audioChunks = [];
let isRecording = false;

const startRecordingBtn = document.getElementById('start-recording');
const stopRecordingBtn = document.getElementById('stop-recording');
const textInput = document.getElementById('text-input');
const sendButton = document.getElementById('send-button');

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        
        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };
        
        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            audioChunks = [];
            await processAudio(audioBlob);
        };
        
        mediaRecorder.start();
        isRecording = true;
        updateUI();
        
    } catch (error) {
        console.error('Error accessing microphone:', error);
        showError('Could not access microphone');
    }
}

function stopRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        isRecording = false;
        updateUI();
    }
}

function updateUI() {
    startRecordingBtn.disabled = isRecording;
    stopRecordingBtn.disabled = !isRecording;
    textInput.disabled = isRecording;
    sendButton.disabled = isRecording;
}

async function processAudio(audioBlob) {
    const formData = new FormData();
    formData.append('audio', audioBlob);
    
    try {
        const response = await fetch('/process_audio', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        if (data.response) {
            addMessage('You: ' + data.text, 'user');
            addMessage('Assistant: ' + data.response, 'assistant');
            playAudioResponse(data.audio_url);
        }
    } catch (error) {
        console.error('Error processing audio:', error);
        showError('Error processing audio');
    }
}

async function sendTextMessage() {
    const input = textInput.value.trim();
    if (!input) return;
    
    addMessage('You: ' + input, 'user');
    textInput.value = '';
    
    try {
        const response = await fetch('/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ input: input })
        });
        
        const data = await response.json();
        if (data.response) {
            addMessage('Assistant: ' + data.response, 'assistant');
            playAudioResponse(data.audio_url);
        }
    } catch (error) {
        console.error('Error sending message:', error);
        showError('Error sending message');
    }
}

function addMessage(message, sender) {
    const chatMessages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    messageDiv.textContent = message;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function playAudioResponse(audioUrl) {
    const audio = new Audio(audioUrl);
    audio.play().catch(error => {
        console.error('Error playing audio:', error);
    });
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    document.body.appendChild(errorDiv);
    setTimeout(() => errorDiv.remove(), 3000);
}

// Event Listeners
startRecordingBtn.addEventListener('click', startRecording);
stopRecordingBtn.addEventListener('click', stopRecording);
sendButton.addEventListener('click', sendTextMessage);
textInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendTextMessage();
    }
});