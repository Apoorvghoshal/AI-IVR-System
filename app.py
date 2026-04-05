from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather
import requests
import os

app = Flask(__name__)

GEMINI_API_KEY = "AIzaSyC4Pmbpb2STDnQcOc_mpRlKxzPjMiI9yJg"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"


@app.route("/voice", methods=['GET', 'POST'])
def voice():
    resp = VoiceResponse()

    gather = Gather(
        input='speech',
        action='https://ai-ivr-system-vesm.onrender.com/process-speech',
        method='POST',
        timeout=5
    )

    gather.say("Welcome to our customer service care. How may I help you?")
    resp.append(gather)

    resp.say("We did not receive any input. Goodbye.")

    return str(resp)


@app.route("/process-speech", methods=['POST'])
def process_speech():
    resp = VoiceResponse()

    user_speech = request.values.get('SpeechResult')

    if not user_speech:
        resp.say("Sorry, I could not hear you. Please try again.")
        resp.redirect('https://ai-ivr-system-vesm.onrender.com/voice')
        return str(resp)

    print("User said:", user_speech)

    # Send to Gemini API
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": user_speech}
                ]
            }
        ]
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        gemini_response = requests.post(GEMINI_URL, json=payload, headers=headers)
        result = gemini_response.json()
        print("Gemini RAW response:", result)

        ai_reply = result['candidates'][0]['content']['parts'][0]['text']

    except Exception as e:
        print("Gemini Error:", e)
        ai_reply = "Sorry, I am facing some technical issues."

    resp.say(ai_reply)

    # Keep conversation going
    resp.redirect('https://ai-ivr-system-vesm.onrender.com/voice')

    return str(resp)


if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
