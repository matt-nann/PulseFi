import telnyx
from flask import request, make_response, jsonify
from pprint import pprint
import base64
import hashlib
import hmac
import time

from src import getSecret

class Telnyx_API:
    def __init__(self, db, csrf):
        telnyx.api_key = getSecret('TELNYX_API_KEY')
        self.db = db
        self.csrf = csrf
    
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
        @self.csrf.exempt
        def sms_webhook():
            """
            Request Headers:
            {'Connect-Time': '0',
            'Connection': 'close',
            'Content-Length': '1360',
            'Content-Type': 'application/json',
            'Host': 'pulse-fi.herokuapp.com',
            'Telnyx-Signature-Ed25519': 'FWUgF9+Dh9kjhN4cXZ+eJOHDs06AJlSxGxEd27Enidsbko6/nrasEhrhgJGxdCvcz1WqBkiVoVuOcLGs/d0nDQ==',
            'Telnyx-Timestamp': '1682370644',
            'Total-Route-Time': '0',
            'User-Agent': 'telnyx-webhooks',
            'Via': '1.1 vegur',
            'X-Forwarded-For': '192.76.120.139',
            'X-Forwarded-Port': '443',
            'X-Forwarded-Proto': 'https',
            'X-Request-Id': 'ec145cea-0077-46d4-9f7c-b9590e49dec0',
            'X-Request-Start': '1682370644993'}
            Request Form Data:
            ImmutableMultiDict([])
            Request JSON Data:
            Request URL Parameters:
            ImmutableMultiDict([])
            """
            # Print request headers
            print("Request Headers:")
            pprint(dict(request.headers))

            # Print request data (form data)
            print("Request Form Data:")
            pprint(request.form)

            # Print request JSON data (if available)
            print("Request JSON Data:")
            # pprint(request.get_json())

            # Print request URL parameters
            print("Request URL Parameters:")
            pprint(request.args)

            """
            Request Headers:
            {'Connect-Time': '0',
            'Connection': 'close',
            'Content-Length': '1360',
            'Content-Type': 'application/json',
            'Host': 'pulse-fi.herokuapp.com',
            'Telnyx-Signature-Ed25519': 'FWUgF9+Dh9kjhN4cXZ+eJOHDs06AJlSxGxEd27Enidsbko6/nrasEhrhgJGxdCvcz1WqBkiVoVuOcLGs/d0nDQ==',
            'Telnyx-Timestamp': '1682370644',
            'Total-Route-Time': '0',
            'User-Agent': 'telnyx-webhooks',
            'Via': '1.1 vegur',
            'X-Forwarded-For': '192.76.120.139',
            'X-Forwarded-Port': '443',
            'X-Forwarded-Proto': 'https',
            'X-Request-Id': 'ec145cea-0077-46d4-9f7c-b9590e49dec0',
            'X-Request-Start': '1682370644993'}
            Request Form Data:
            ImmutableMultiDict([])
            Request JSON Data:
            Request URL Parameters:
            ImmutableMultiDict([])
            """
            
            try:
                sms_from = request.form['from']
                sms_to = request.form['to']
                sms_text = request.form['text']
            except:
                return make_response(jsonify({'error': 'did not specify sending and receiving numbers'}), 200)
            print(f"Received SMS from {sms_from} to {sms_to} with text: {sms_text}")

            # # # Extract the Google 2FA code from the SMS text
            # # # assuming the message contains only the code
            # google_2fa_code = sms_text.strip()
            print(sms_text)

            # Use the extracted 2FA code to complete the login process
            # by interacting with the browser instance
            # (e.g., input the code in the appropriate field and submit the form)
            self.forwardMessage(sms_text)
            # jsonify({'error': 'No songs found in playlists for this mode'})
            return make_response("OK", 200)
            """
            Hierarchy of URLs - Telnyx first tries the primary URL on your Messaging Profile. If that URL does not resolve, or your application returns a response other than an "200 OK", the webhook will be delivered to the failover URL, if one has been specified.
            """

        # @app.route('/forwardSMS', methods=['POST'])
        # def sms_webhook():
        #     # Retrieve the incoming message payload
        #     sms_data = request.json

        #     # Extract the X-Telnyx-Signature header
        #     telnyx_signature_header = request.headers.get('X-Telnyx-Signature')

        #     # Check if the signature header is present
        #     if not telnyx_signature_header:
        #         return jsonify({"error": "Missing Telnyx signature header"}), 400

        #     # Extract the timestamp and signature from the header
        #     timestamp, signature = None, None
        #     for part in telnyx_signature_header.split(','):
        #         key, value = part.split('=')
        #         if key == 't':
        #             timestamp = int(value)
        #         elif key == 'h':
        #             signature = value

        #     # Check if the timestamp and signature were found
        #     if timestamp is None or signature is None:
        #         return jsonify({"error": "Invalid Telnyx signature header"}), 400

        #     # Verify the timestamp
        #     current_timestamp = int(time.time())
        #     if current_timestamp - timestamp > 300:  # 5 minutes
        #         return jsonify({"error": "Expired timestamp"}), 400

        #     # Verify the signature
        #     signing_secret = 'your_signing_secret'  # Replace with your actual signing secret
        #     payload = f'{timestamp}.{".".join(request.get_data().decode())}'
        #     computed_signature = hmac.new(signing_secret.encode(), payload.encode(), hashlib.sha256)
        #     encoded_signature = base64.b64encode(computed_signature.digest()).decode()

        #     if signature != encoded_signature:
        #         return jsonify({"error": "Invalid signature"}), 400

        #     # Process the SMS data
        #     print(sms_data)

        #     return jsonify({"result": "SMS received and processed"}), 200

        return app