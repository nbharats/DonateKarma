from email.message import EmailMessage
import smtplib

app='scym ddzd pscw fdlz'

def send_mail(subject,to,body):
    server=smtplib.SMTP_SSL('smtp.gmail.com',465)
    server.login('bsn41003@gmail.com',app)
    msg=EmailMessage()
    msg['TO']=to
    msg['FROM']='bsn41003@gmail.com'
    msg['SUBJECT']=subject
    msg.set_content(body)
    server.send_message(msg=msg)
    server.close()

