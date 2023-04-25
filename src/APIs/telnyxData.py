import telnyx
from flask import request, make_response, jsonify
from pprint import pprint
import json

from src import getSecret

class Telnyx_API:
    TOLERANCE_SECONDS = 5 * 60 # 5 minutes
    def __init__(self, db, csrf):
        telnyx.api_key = getSecret('TELNYX_API_KEY')
        telnyx.public_key = getSecret('TELNYX_PUBLIC_KEY')
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
    def verify_signature(self, request):
        try:
            body = request.data.decode('utf-8')
        except:
            return "Bad payload", 400

        signature = request.headers.get("Telnyx-Signature-ed25519", None)
        timestamp = request.headers.get("Telnyx-Timestamp", None)

        print("Payload:", json.dumps(body))
        print("Signature:", signature)
        print("Timestamp:", timestamp)

        if not signature or not timestamp:
            return "No signature or timestamp", 400

        try:
            event = telnyx.Webhook.construct_event(body, signature, timestamp, self.TOLERANCE_SECONDS)
        except ValueError:
            print("Error while decoding event!")
            return "Bad payload", 400
        except telnyx.error.SignatureVerificationError as err:
            pprint("SignatureVerificationError: " + str(err))
            return "Bad signature", 400  
        return event, 200 

    def add_routes(self, app, db, spotify_and_fitbit_authorized_required):
        
        @app.route('/forwardSMS', methods=['POST'])
        @self.csrf.exempt
        def sms_webhook():
            """
            {
                "data": {
                    "event_type": "message.received",
                    "id": "22a7457f-90e3-441e-8832-339cd7755a86",
                    "occurred_at": "2023-04-25T16:54:55.796+00:00",
                    "payload": {
                        "autoresponse_type": null,
                        "cc": [],
                        "completed_at": null,
                        "cost": null,
                        "direction": "inbound",
                        "encoding": "GSM-7",
                        "errors": [],
                        "from": {
                            "carrier": "Verizon Wireless",
                            "line_type": "Wireless",
                            "phone_number": "+17743642453"
                        },
                        "id": "49bbfe3c-7fb3-496d-ac59-6e80c708a526",
                        "media": [],
                        "messaging_profile_id": "40017f0f-92d8-4318-9f8a-e0e2a92c3f60",
                        "organization_id": "82fc37e7-63d3-4165-9b54-855ee8caa737",
                        "parts": 1,
                        "received_at": "2023-04-25T16:54:55.690+00:00",
                        "record_type": "message",
                        "sent_at": null,
                        "subject": "",
                        "tags": [],
                        "text": "Testing 12:54",
                        "to": [
                            {
                                "carrier": "Telnyx",
                                "line_type": "Wireless",
                                "phone_number": "+16182721034",
                                "status": "webhook_delivered"
                            }
                        ],
                        "type": "SMS",
                        "valid_until": null,
                        "webhook_failover_url": null,
                        "webhook_url": "https://pulse-fi.herokuapp.com/forwardSMS"
                    },
                    "record_type": "event"
                },
                "meta": {
                    "attempt": 1,
                    "delivered_to": "https://pulse-fi.herokuapp.com/forwardSMS"
                }
            }
            """
            print("Request Headers:")
            try:
                pprint(request.headers)
            except:
                print("No headers found")
            print("Request Form Data:")
            try:
                pprint(request.form)
            except:
                print("No form data found")
            print("Request JSON Data:")
            try:
                pprint(request.get_json())
            except:
                print("No JSON data found")
            print("Request URL Parameters:")
            try:
                pprint(request.args)
            except:
                print("No URL parameters found")   

            event, status = self.verify_signature(request)
            if status != 200:
                print("Signature verification failed error message: ", event)
                return event, status
            
            body = json.loads(request.data)
            
            # ignore outgoing messages
            from_number = body["data"]["payload"]["from"]["phone_number"]
            if from_number == getSecret('TELNYX_NUMBER'):
                return make_response("OK", 200)

            message_id = body["data"]["payload"]["id"]
            to_number = body["data"]["payload"]["to"][0]["phone_number"]
            sms_text = body["data"]["payload"]["text"]

            print("message_id : ", message_id, "SMS from: " + from_number, "to: " + to_number, "message: " + sms_text)
            self.forwardMessage(sms_text)

            return make_response("OK", 200)
            """
            Hierarchy of URLs - Telnyx first tries the primary URL on your Messaging Profile. If that URL does not resolve, or your application returns a response other than an "200 OK", the webhook will be delivered to the failover URL, if one has been specified.
            """

        return app