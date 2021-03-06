import sys
import mailbox
import email
from datetime import datetime

import web
import config
from settings import db

MAILDIR_PATH = config.maildir_path

def getid(msg):
    to = msg.get('To')
    if not to.startswith('p-'): return
    id = email[email.index('p-')+2 : email.index('@')]
    return int(id, 36)
    
def format_date(date):
    """
        >>> date = 'Fri, 22 Aug 2008 11:38:05 +0530 (IST)'
        >>> format_date(date)
        datetime.datetime(2008, 8, 22, 11, 38, 5)
    """
    date = msg.get('Date')
    date = date[0:date.index(' +')] #@@ FIX IT - loosing timezone info
    return datetime.strptime(date, '%a, %d %b %Y %H:%M:%S')
    
def get_msg_body(msg):    
    if msg.is_multipart():
        msgbody = "\n".join(m.get_payload().strip() for m in msg)
    else:
        msgbody = msg.get_payload().strip()
    return msgbody
    
def process(msg):
    #store the msg in db and send followup msg to the signatory
 
    wyr_id = getid(msg)
    if not signid: return
    msgbody = get_msg_body(msg)
    received = format_date(msg.get('Date')) #msg.get_date() doesn't work!!
    
    try:
        db.insert('wyr_responses', wyr_id=wyr_id, response=msgbody, received=received)
    except Exception, details:
        print 'Error:', details
    else:
        send_followup(wyr_id, response_body)

def get_user_email(wyrid):
    if (wyrid % 2): #odd wyrid => msg is from signature of a petition to congress
        wyrid = (wyrid - 1)/2
        tables = ['signatory', 'users']
        where = 'signatory.user_id=users.id and signatory.id=$wyrid'
    else: #even wyr_id => msg is from /writerep
        wyrid = wyrid/2
        tables = ['wyr', 'users']
        where = 'wyr.sender=users.id and wyr.id=$wyr.id'

    to_addr = db.select(tables, what='users.email', where=where, vars=locals())
    if to_addr:
        return to_addr[0].email
    
        
def send_followup(wyr_id, response_body):
    from_addr = config.from_address
    to_addr = get_user_email(wyr_id)
    subject = 'FILL IN HERE'
    body = response_body +  'FILL IN HERE'                   
    web.sendmail(from_addr, to_addr, subject, body)
    
if __name__ == '__main__':
    inbox = mailbox.Maildir(MAILDIR_PATH, factory=mailbox.MaildirMessage, create=False)

    for msg in inbox.itervalues():
        process(msg)
