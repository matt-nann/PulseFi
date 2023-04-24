from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/sms', methods=['POST'])
def sms_webhook():
    sms_from = request.form['from']
    sms_to = request.form['to']
    sms_text = request.form['text']

    print(f"Received SMS from {sms_from} to {sms_to} with text: {sms_text}")

    # Extract the Google 2FA code from the SMS text
    # assuming the message contains only the code
    google_2fa_code = sms_text.strip()

    # Use the extracted 2FA code to complete the login process
    # by interacting with the browser instance
    # (e.g., input the code in the appropriate field and submit the form)

    return '', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
