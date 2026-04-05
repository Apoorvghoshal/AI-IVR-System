# Download the helper library from https://www.twilio.com/docs/python/install
import os

from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather

app = Flask(__name__)


@app.route("/voice", methods=['GET', 'POST'])
def voice():
    resp = VoiceResponse()

    # Gather input from user (DTMF tones)
    gather = Gather(
        num_digits=1,
        action='/handle-key',
        method='POST'
    )

    gather.say(
        "Welcome to Apoorv's IVR system. "
        "Press 1 for help. "
        "Press 2 for good morning. "
        "Press 3 for good afternoon."
    )

    resp.append(gather)

    # If no input received
    resp.say("We did not receive any input. Goodbye!")

    return str(resp)


@app.route("/handle-key", methods=['GET', 'POST'])
def handle_key():
    resp = VoiceResponse()

    digit_pressed = request.values.get('Digits', None)

    if digit_pressed == '1':
        resp.say("How may I help you?")

    elif digit_pressed == '2':
        resp.say("Good morning!")

    elif digit_pressed == '3':
        resp.say("Good afternoon!")

    else:
        resp.say("Invalid input. Please try again.")
        resp.redirect('/voice')  # Go back to menu

    return str(resp)



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
