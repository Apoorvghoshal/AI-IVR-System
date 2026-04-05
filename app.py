from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather
import requests
import os

app = Flask(__name__)


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
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
                {
                    "text": f"""
You are a polite and professional customer care assistant for APEX Hospital.

Hospital Details:
- Services: General Checkup, Emergency Care, Cardiology, Orthopedics, Neurology
- Address: MG Road, Raipur
- Reception: +91 9876543210

Rules:
- Answer in 1-2 sentences
- Be polite and human-like
- If conversation is complete, add END
- If more help needed, add CONTINUE

Examples:
User: Thank you
Response: You're welcome! Have a great day. END

User: I want to book appointment
Response: Sure, please tell me your preferred department. CONTINUE

User query: {user_speech}
"""
                }
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

# Check if END or CONTINUE
        if "END" in ai_reply:
            clean_reply = ai_reply.replace("END", "").strip()
            resp.say(clean_reply)
            resp.say("Thank you for calling APEX Hospital. Goodbye.")
            resp.hangup()

        else:
            clean_reply = ai_reply.replace("CONTINUE", "").strip()
            resp.say(clean_reply)

        # Ask again
        gather = Gather(
            input='speech',
            action='https://ai-ivr-system-vesm.onrender.com/process-speech',
            method='POST',
            timeout=5
        )
        gather.say("Is there anything else I can help you with?")
        resp.append(gather)
    
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
