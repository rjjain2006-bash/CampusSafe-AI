import os
import base64
import webbrowser
from threading import Timer
from flask import Flask, request, jsonify, send_from_directory
from google import genai
from google.genai import types

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)

# ==========================================
# PASTE YOUR ACTUAL GEMINI API KEY HERE:
# ==========================================
API_KEY = "AQ.Ab8RN6KvnAijwnM4WkOfEFWkiIu1gYiegyPDZ4j6R3MCVEEEtA"

@app.route('/')
def index():
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        if not API_KEY or API_KEY == "YOUR_GEMINI_API_KEY_HERE":
            return jsonify({'success': False, 'error': 'API key is missing in app.py'}), 500

        client = genai.Client(api_key=API_KEY)
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data received'}), 400

        prompt = data.get('prompt', '')
        language = data.get('language', 'English')
        image_base64 = data.get('imageBase64')

        if not prompt and not image_base64:
            return jsonify({'success': False, 'error': 'Provide text or an image'}), 400

        system_instruction = (
            f"You are CampusSafe AI, an expert, calm health and safety triage assistant. "
            f"Respond clearly and concisely in {language}. "
            f"Structure your response with clear headings: 1. Assessment, 2. Immediate Action, 3. Next Steps. "
            f"Always remind the user to contact professional medical emergency services if symptoms worsen."
        )

        contents = [f"User Situation / Request: {prompt}"]

        if image_base64:
            if ',' in image_base64:
                image_base64 = image_base64.split(',')[1]
            image_bytes = base64.b64decode(image_base64)
            contents.append(types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"))

        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.3,
            )
        )

        return jsonify({'success': True, 'result': response.text})

    except Exception as e:
        print(f"🔥 GEMINI ERROR: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("Server running on http://localhost:3000 - Opening browser automatically...")
    Timer(1, lambda: webbrowser.open("http://localhost:3000")).start()
    app.run(host='127.0.0.1', port=3000, debug=False)
