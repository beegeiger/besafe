from twilio.rest import Client
from secrets import twilio_token
account_sid = 'AC9be9fab60c188959499aee8101059896'
auth_token = twilio_token
client = Client(account_sid, auth_token)

def send_twilio_sms(recipient, content):
    message = client.messages.create(
                                  messaging_service_sid='MG56f27c44ea5c19616a38262fdd2b5d27',
                                  body=content,
                                  to='+1' + recipient
                              )

    print(message.sid)
    return
