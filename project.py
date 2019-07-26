import base64
import email

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'

def main():
   
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('gmail', 'v1', http=creds.authorize(Http()))
    
    # Call the Gmail API to fetch INBOX
    results = service.users().messages().list(userId='me',labelIds = ['INBOX']).execute()
    messages = results.get('messages', [])
    
    if not messages:
        print("No messages found.")
    else:
        print("Message snippets:")
        for m in messages:
            message = service.users().messages().get(userId='me', id=m['id'], format='raw').execute()
            msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
            # print(str(msg_str))

            mime_msg = email.message_from_string(str(msg_str))

            print(mime_msg)
            # msg = service.users().messages().get(userId='me', id=message['id'], format = 'full').execute()
            # email_str = msg['snippet']
            # print(msg.keys())

if __name__ == '__main__':
    main()