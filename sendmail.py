import smtplib
from email.message import EmailMessage
from email import utils
from dns import resolver
import dkim
import time
import random

resolver = resolver.Resolver()


def generate_message_id(domain):
    timestamp = int(time.time() * 10e5)
    unique_id = f"{timestamp}.{random.randint(10000, 99999)}"
    return f"<{unique_id}@{domain}>"


def domain_from_address(address):
    return address.split('@')[1]


def get_mx(address):
    domain = domain_from_address(address)
    records = resolver.resolve(domain, 'MX')
    return str(records[0].exchange)


def sendmail(sender, recipient, mail_from, subject, body, dkim_conf, tls=True, dsn=False):
    mx = get_mx(recipient)

    # create mail
    msg = EmailMessage()

    # setup headers here
    msg['Message-ID'] = generate_message_id(domain_from_address(sender))
    msg['Date'] = utils.formatdate(localtime=True)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient

    msg.set_content(body)

    if dkim_conf:
        msg_bytes = msg.as_bytes()

        dkim_header = dkim.sign(
            msg_bytes,
            selector=dkim_conf['selector'].encode('utf-8'),
            domain=dkim_conf['domain'].encode('utf-8'),
            privkey=dkim_conf['privkey'].encode('utf-8'),
        )

        msg['DKIM-Signature'] = ''.join(
            dkim_header.decode().split('\r\n'))[16:]

    print(msg)

    with smtplib.SMTP(mx) as smtp:
        helo_domain = "sender." + domain_from_address(mail_from)

        if tls:
            _, exts = smtp.ehlo()
            if 'STARTTLS' in exts.decode():
                print('Initiating STARTTLS')
                smtp.starttls()

        smtp.ehlo(helo_domain)
        print('Sending...')

        if dsn:
            smtp.send_message(msg, mail_from, [recipient], mail_options=['RET=HDRS', f'ENVID = {
                int(random.random() * 10e6)}'], rcpt_options=['NOTIFY = SUCCESS, FAILURE, DELAY'])
        else:
            smtp.send_message(msg, mail_from, [recipient])


if __name__ == '__main__':

    mail_file = ''
    privkey_file = ''

    with open(privkey_file, 'r') as file:
        privkey = file.read()

    with open(mail_file, 'r') as file:
        body = file.read()

    dkim_conf = {
        'privkey': privkey,
        'selector': '',
        'domain': ''
    }

    sendmail(
        sender='',
        recipient='',
        mail_from='',
        subject='',
        body=body,
        dkim_conf=None
    )
