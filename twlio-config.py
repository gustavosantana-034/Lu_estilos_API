from dotenv import load_dotenv
import os
from twilio.rest import Client
load_dotenv()


account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
from_whatsapp = os.getenv("TWILIO_WHATSAPP_NUMBER")
content_sid = os.getenv("TWILIO_WHATSAPP_CONTENT_SID")


client = Client(account_sid, auth_token)


message = client.messages.create(
    from_=from_whatsapp,
    content_sid=content_sid,
    content_variables='{"1":"12/1","2":"3pm"}',
    to='whatsapp:+5512992103808'
)

print(message.sid)
