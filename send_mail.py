import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from socket import gaierror
import time
import config

fromaddr = config.fromaddr
pw = config.pw
smtp_host = config.smtp_host
imap_host = config.imap_host
history_gaierror = 0


def send_email(se_subject, se_body, se_to):
    print("send_email start")
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = ", ".join(se_to)  # muss ein String sein, darf keine List sein
    msg['Subject'] = se_subject

    msg.attach(MIMEText(se_body, 'plain'))
    global history_gaierror
    try:
        server = smtplib.SMTP_SSL(smtp_host, 465)
    except gaierror as send_email_error_text:
        print("Socket.gaierror beim Senden von Emails (Error-Meldung: " + str(send_email_error_text) + ")",
              repr(send_email_error_text) + " (senden) am " + time.strftime("%d.%m.%y %H:%M:%S (%A)",
                                                                            time.localtime()))
        history_gaierror += 1
        time.sleep(10)
        send_email(se_subject=se_subject, se_body=se_body, se_to=se_to)
    else:
        history_gaierror = 0
        server.login(fromaddr, pw)
        server.sendmail(fromaddr, se_to, msg.as_string())
        server.quit()
