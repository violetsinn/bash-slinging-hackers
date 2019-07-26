import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import string
from collections import Counter
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import base64
import email

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
# get_ipython().run_line_magic('matplotlib', 'inline')

import seaborn as sns
sns.set(style = "whitegrid", 
        color_codes = True,
        font_scale = 1.5)

import warnings 
warnings.filterwarnings('ignore')




def getSpamWords():

    f = open("word_list.dat","r")
    contents = f.readlines()
    contents = [i.strip()[1:] for i in contents]
   
    # contents = ['winning', 'win', 'please', 'offer', 'contact', 'rates', 'death', 'dear', 'remove', 'guarantee', '$', '$$', '$$$', 'click', 'credit', 'cash', '!!', '!!!', '%', 'transfer', 'visit', 'body']
    return contents




def connect_to_gmail():

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
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            # print("KEYS)")
            convertText = msg["payload"]["parts"][0]["body"]["data"]
            msg_str = base64.urlsafe_b64decode(convertText).decode("utf-8")

            msg_str = msg_str.lower()
            return msg_str
        # for m in messages:3
        #     message = service.users().messages().get(userId='me', id=m['id'], format='raw').execute()
            
        #     # print(str(msg_str))

        #     mime_msg = email.message_from_string(str(msg_str))

        #     return mime_msg
            # msg = service.users().messages().get(userId='me', id=message['id'], format = 'full').execute()
            # email_str = msg['snippet']
            # print(msg.keys())



def words_in_texts(words, texts):
    '''
    Args:
        words (list-like): words to find
        texts (Series): strings to search in
    
    Returns:
        NumPy array of 0s and 1s with shape (n, p) where n is the
        number of texts and p is the number of words.
    '''
    indicator_array = np.array([[word in text for word in words] for text in texts])
    return indicator_array

def checkSpam(word_list, email):
    email = email.lower()

    original_training_data = pd.read_csv('data/train.csv')
    original_training_data['email'] = original_training_data['email'].str.lower()
    original_training_data = original_training_data.fillna(" ")

    from sklearn.model_selection import train_test_split
    [train, val] = train_test_split(original_training_data, test_size=0.1)

    def feature_matrix(words, texts):
        '''
        Args:
            words (list-like): words to find
            texts (Series): strings to search in
        
        Returns:
            NumPy array of 0s and 1s with shape (n, p) where n is the
            number of texts and p is the number of words.
        '''
        indicator_array = np.array([[(word in text) & (len(text) < 22000) for word in words] for text in texts])
        return indicator_array

    from sklearn.linear_model import LogisticRegression

    phi_train = feature_matrix(word_list, train['email'])
    y_train = train['spam']

    model = LogisticRegression().fit(phi_train, y_train)
    return model.predict(feature_matrix(word_list, email))



def main():

    sendTo = "v.a.sinnarkar@berkeley.edu"
    gmail_user = 'humsincident@gmail.com'
    gmail_password = 'humana$1'
    spam_msg = "This message is likely to be spam!"
    phish_msg = "This message is likely to be a phishing email!"
    sender_msg = "This message is likely to be sent from a non-trustworthy source."
    
    #REPLACE THESE WITH FUNCTION CALLS

    # word_list = ['guaranteed', 'today', 'winner', 'easy', 'simple']
    # email_content = ["Here is a random message that should not be spam"]

    # print("trying to connect to gmail")
    # print(connect_to_gmail())


    email_content = connect_to_gmail()

    word_list = getSpamWords()

    print("Email: ", email_content)
    print("Spam words: ", word_list)

    # print("\n That's the connection to gmail")

    if 0 == checkSpam(word_list, email_content)[0]:
        print("This email is clean")
        spam = False
        
    else:
        print("This email is SPAMMMMM")
        spam = True 

    # TODO : Replace with actual code 

   
    phish = False
    sender = False
    email = ""
    context = ssl.create_default_context()

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls(context=context)
        server.login(gmail_user, gmail_password)

        if spam == True:
            email += spam_msg+ "<br>" 
        if phish == True:
            email += phish_msg+ "<br>" 
        if sender == True:
            email += sender_msg+ "<br>" 

        if email == "":
            # server.sendmail('humsincident@gmail.com', sendTo, "This is a clean email my d00der")
            print("Clean email sent!")
            
        else:
            # server.sendmail('humsincident@gmail.com', sendTo, email)
            print("Spam email sent!")
            
        server.close()

    except:
        print('Something went wrong...')

if __name__ == '__main__':
    main()



