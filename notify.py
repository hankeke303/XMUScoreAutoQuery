from plyer import notification
import yaml
import smtplib
from email.mime.text import MIMEText
from email.header import Header

with open('config.yaml', 'r', encoding='utf-8') as f:
    conf = yaml.load(f, Loader=yaml.FullLoader)
    smtp_conf = conf['email']
    notify_type = conf['notify']

def report_with_smtp(title, message):
    try:
        host = smtp_conf['host']
        port = smtp_conf['port']
        username = smtp_conf['username']
        password = smtp_conf['password']
        receiver = smtp_conf.get('receiver', username)
        use_ssl = smtp_conf.get('use_ssl', False)
        assert host != None and port != None and username != None and password != None
        if receiver == None:
            receiver = username

        msg = MIMEText(message, 'plain', 'utf-8')
        msg['Subject'] = title
        msg['From'] = '%s <%s>' % (Header("成绩提醒", 'utf-8').encode(), username)
        msg['To'] = Header(receiver if isinstance(receiver, str) else ",".join(receiver), 'utf-8')

        print(msg)

        try:
            smtp = smtplib.SMTP_SSL(host, port) if use_ssl else smtplib.SMTP(host, port)
            smtp.login(username, password)
            smtp.sendmail(username, receiver, msg.as_string())
        except smtplib.SMTPException:
            print("Error: 发送邮件失败")
            raise
    except KeyError:
        print("Cannot report with SMTP: some secret_key not set")
        return
    except Exception:
        raise

def notify(title, message):
    if notify_type == 'email' or notify_type == 'both':
        report_with_smtp(title, message)
    if notify_type == 'both' or notify_type == 'system':
        notification.notify(
            title = title,
            message = message[:256],
            app_icon = None,
            timeout = 10
        )

if __name__ == "__main__":
    report_with_smtp('嘿嘿嘿', '哇哇哇')