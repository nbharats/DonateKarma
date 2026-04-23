from email.message import EmailMessage
import smtplib

app='nxkw djsm bbqs onex'

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

def send_invoice_mail(subject,to,body,attachment,filename):
    server=smtplib.SMTP_SSL('smtp.gmail.com',465)
    server.login('bsn41003@gmail.com',app)
    msg=EmailMessage()
    msg['TO']=to
    msg['FROM']='bsn41003@gmail.com'
    msg['subject']=subject
    msg.set_content(body)
    msg.add_attachment(
            attachment,
            maintype='application',
            subtype='pdf',
            filename=filename
        )
    server.send_message(msg=msg)
    server.close()