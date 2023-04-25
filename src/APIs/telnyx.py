import telnyx
from flask import request, make_response, jsonify
from pprint import pprint
import base64
import hashlib
import hmac
import time
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.exceptions import InvalidSignature
import base64
import textwrap

from src import getSecret

def to_text(value, encoding='utf-8'):
    """Convert value to unicode, default encoding is utf-8

    :param value: Value to be converted
    :param encoding: Desired encoding
    """
    if not value:
        return ''
    if isinstance(value, str):
        return value
    if isinstance(value, bytes):
        return value.decode(encoding)
    return str(value)

def to_binary(value, encoding='utf-8'):
    """Convert value to binary string, default encoding is utf-8

    :param value: Value to be converted
    :param encoding: Desired encoding
    """
    if not value:
        return b''
    if isinstance(value, bytes):
        return value
    if isinstance(value, str):
        return value.encode(encoding)
    return to_text(value).encode(encoding)

class Telnyx_API:
    def __init__(self, db, csrf):
        telnyx.api_key = getSecret('TELNYX_API_KEY')
        self.db = db
        self.csrf = csrf
        self.public_key = getSecret('TELNYX_PUBLIC_KEY')
    
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
            # Print request headers
            print("Request Headers:")
            pprint(dict(request.headers))

            headers = dict(request.headers)
            timestamp = headers['Telnyx-Timestamp']
            signature = headers['Telnyx-Signature-Ed25519']

            # Print request data (form data)
            print("Request Form Data:")
            try:
                pprint(request.form)
            except:
                print("No form data found")

            # Print request JSON data (if available)
            print("Request JSON Data:")
            try:
                pprint(request.get_json())
            except:
                print("No JSON data found")

            # Print request URL parameters
            print("Request URL Parameters:")
            try:
                pprint(request.args)
            except:
                print("No URL parameters found")
            
            body = request.data.decode("utf-8")
            signature = request.headers.get("Telnyx-Signature-ed25519", None)
            timestamp = request.headers.get("Telnyx-Timestamp", None)

            try:
                event = telnyx.Webhook.construct_event(body, signature, timestamp, self.public_key)
            except ValueError:
                print("Error while decoding event!")
                return "Bad payload", 400
            except telnyx.error.SignatureVerificationError:
                print("Invalid signature!")
                return "Bad signature", 400

            print("Received event: id={id}, type={type}".format(id=event.id, type=event.type))

            # Return a 200 OK response to acknowledge receipt of the webhook
            return jsonify({'status': 'success'}), 200
        
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

            headers = dict(request.headers)
            timestamp = headers['Telnyx-Timestamp']
            signature = headers['Telnyx-Signature-Ed25519']

            # Print request data (form data)
            print("Request Form Data:")
            pprint(request.form)

            # Print request JSON data (if available)
            print("Request JSON Data:")
            try:
                pprint(request.get_json())
            except:
                print("No JSON data found")

            # Print request URL parameters
            print("Request URL Parameters:")
            pprint(request.args)
            
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
    

# import base64
# from flask import Flask, request, jsonify
# from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
# from cryptography.hazmat.primitives.serialization import load_pem_public_key
# from cryptography.exceptions import InvalidSignature

# app = Flask(__name__)

# # Replace this with your Telnyx public key in PEM format
# TELNYX_PUBLIC_KEY_PEM = b"""-----BEGIN PUBLIC KEY-----
# your_public_key_here
# -----END PUBLIC KEY-----"""

# # Load the public key
# public_key = load_pem_public_key(TELNYX_PUBLIC_KEY_PEM)

# @app.route('/webhook', methods=['POST'])
# def webhook():
#     # Get the webhook payload from the incoming request
#     payload = request.data

#     # Get the signature and timestamp headers
#     signature = request.headers.get('Telnyx-Signature-Ed25519')
#     timestamp = request.headers.get('Telnyx-Timestamp')

#     if not signature or not timestamp:
#         return jsonify({"status": "error", "message": "Missing signature or timestamp headers"}), 400

#     # Verify the signature
#     signed_payload = timestamp.encode('utf-8') + b'|' + payload

#     try:
#         decoded_signature = base64.b64decode(signature)
#         public_key.verify(decoded_signature, signed_payload)
#     except InvalidSignature:
#         return jsonify({"status": "error", "message": "Invalid signature"}), 401

#     # Process the payload
#     data = request.get_json()
#     text_message = data.get('data', {}).get('payload', {}).get('text', '')
#     print(f"Received text message: {text_message}")

#     # Return a 200 OK response to acknowledge receipt of the webhook
#     return jsonify({'status': 'success'}), 200

# if __name__ == '__main__':
#     app.run()
