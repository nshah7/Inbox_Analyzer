from __future__ import print_function
import httplib2
import os

import time
from ISStreamer.Streamer import Streamer

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

class freq(dict):
	def __missing__(self, key):
		return 0

def main():
    """Shows basic usage of the Gmail API.

    Creates a Gmail API service object and outputs a list of label names
    of the user's Gmail account.
    """
    isf = freq()
    sf = freq()

    streamer = Streamer(bucket_name="SpamCan", bucket_key="BDME93PFX86R", access_key="fIerazeNgnzhc3rVIzkwQLzrDN8MIe0a")
    
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)
    results = service.users().messages().list(userId='me', includeSpamTrash = True).execute()
    threads = results.get('messages')
    senders = []
    total = 0
    if not threads:
        print("No threads found")
        return
    else:
        print("Threads:")
        for thread in threads:
            msg_id = thread['id']
            message = service.users().messages().get(userId = "me", id = msg_id, format = 'full').execute()
            if not message:
                print('No messages found.')
                return
            else:
                headers = message['payload']['headers']
                for i in range(len(headers)):
                        if headers[i]['name'] == 'From':
                            indexl = (headers[i]['value'].rfind('@'))
                            indexr = (headers[i]['value'].rfind('>'))
                            sender = headers[i]['value'][indexl+1:indexr]
                            print(sender)
                            time.sleep(0.1)
                            if sender not in sf:
                                sf[sender] = 1
                                total += 1
                                streamer.log(sender, sf[sender])
                                streamer.log("Total", total)
                            else:
                                sf[sender] += 1
                                total += 1
                                streamer.log(sender, sf[sender])
                                streamer.log("Total", total)

if __name__ == '__main__':
    main()
