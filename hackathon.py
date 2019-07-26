import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import string
from collections import Counter
import numpy as np
import pandas as pd

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

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

   
    contents = ['winning', 'win', 'please', 'offer', 'contact', 'rates', 'death', 'dear', 'remove', 'guarantee', '$', '$$', '$$$', 'click', 'credit', 'cash', '!!', '!!!', '%', 'transfer', 'visit', 'body']
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
            # print(msg["payload"])
            # print(msg["raw"])
            # print(msg["payload"]["body"]["data"])
            if "parts" not in msg["payload"].keys():

                convertText = base64.urlsafe_b64decode(msg["payload"]["body"]["data"]).decode("utf-8")
            else:
                convertText =  base64.urlsafe_b64decode(msg["payload"]["parts"][0]["body"]["data"]).decode("utf-8")
            
            emailSender = ""
            for i in msg["payload"]["headers"]:
                if "name" in i:
                    if i["name"] == "From":
                        emailSender = i["value"]

            # if msg["payload"]["headers"]["name"] == "From":
            #     emailSender = msg["payload"]["headers"]["value"]
            # else:
            #     print("Error")
            # emailSender = base64.urlsafe_b64decode(emailSender).decode("utf-8")
            print(emailSender)
            # msg_str = msg_str.lower()
            # emailSender =  base64.urlsafe_b64decode(emailSender).decode("utf-8")
            # print(emailSender)
            return convertText, emailSender
       



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
    
    original_training_data = pd.read_csv('data/train.csv')
    test = pd.read_csv('data/test.csv')

    original_training_data['email'] = original_training_data['email'].str.lower().fillna(" ")
    
    [train, val] = train_test_split(original_training_data, test_size=0.1)
    
    phi_train = feature_matrix(word_list, train['email'])
    y_train = train['spam']

    model = LogisticRegression().fit(phi_train, y_train)
    return int(model.predict(feature_matrix(word_list, [email])))



def main():

    sendTo = "v.a.sinnarkar@berkeley.edu"
    gmail_user = 'humsincident@gmail.com'
    gmail_password = 'humana$1'
    spam_msg = "This message is likely to be spam!"
    phish_msg = "This message is likely to be a phishing email!"
    sender_msg = "This message is likely to be sent from a non-trustworthy source."


    email_content, sendTo = connect_to_gmail() # Gets most recent email from gmail 

    print("Sending to: ", sendTo)
    word_list = getSpamWords() # Receives list of spam words
    
    # Returns a 0 if spam 
    if 0 == checkSpam(word_list, email_content):
        print("This email is clean")
        spam = False
        
    else:
        print("This email is Spam")
        spam = True 

    # TODO : Replace with actual code 


    email = ""
    context = ssl.create_default_context()

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls(context=context)
        server.login(gmail_user, gmail_password)

        if spam == True:
            email += spam_msg+ "<br>" 
        
        if email == "":
            server.sendmail('humsincident@gmail.com', sendTo, "This is a clean email")
            print("Clean Email")
            
        else:
            server.sendmail('humsincident@gmail.com', sendTo, email)
            print("Spam email sent!")
            
        server.close()

    except:
        print('Something went wrong...')

if __name__ == '__main__':
    main()



