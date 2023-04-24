import telnyx
from flask import request

from src import getSecret

class Telnyx_API:
    def __init__(self, db):
        telnyx.api_key = getSecret('TELNYX_API_KEY')
        self.db = db
    
    def forwardMessage(self, message):
        your_telnyx_number = getSecret('TELNYX_NUMBER')
        destination_number = getSecret('PERSONAL_NUMBER')
 
        telnyx.Message.create(
            from_=your_telnyx_number,
            to=destination_number,
            text=message,
        )

    def add_routes(self, app, db, spotify_and_fitbit_authorized_required):
        
        @app.route('/forwardSMS', methods=['POST'])
        def sms_webhook():
            sms_from = request.form['from']
            sms_to = request.form['to']
            sms_text = request.form['text']

            print(f"Received SMS from {sms_from} to {sms_to} with text: {sms_text}")

            # # Extract the Google 2FA code from the SMS text
            # # assuming the message contains only the code
            # google_2fa_code = sms_text.strip()
            print(sms_text)

            # Use the extracted 2FA code to complete the login process
            # by interacting with the browser instance
            # (e.g., input the code in the appropriate field and submit the form)

            self.forwardMessage(sms_text)

            return '', 200

        return app