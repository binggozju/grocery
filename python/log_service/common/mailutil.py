#!/usr/bin/python
# coding=utf-8
"""
mail utility
"""

import os.path
import smtplib
from email.Header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

smtp_server = "smtp.exmail.qq.com"
sender_address = ""
sender_passwd = ""

def init(address, passwd):
    global sender_address, sender_passwd
    sender_address = address
    sender_passwd = passwd
    print "init the mailutil module successfully"

def send_email(subject, content, attachments, receivers):
    """
    @attachments, a list of file names (with full path) 
    @receivers, a string made up of all receiver address, splited by ";"
    """
    mail = MIMEMultipart()
    mail["Subject"] = subject
    mail["From"] = sender_address
    mail["To"] = receivers

    # 正文
    body = MIMEText(content, _subtype='html', _charset='utf-8')
    mail.attach(body)

    # 附件
    for file_name in attachments:
        attach_file = MIMEText(open(file_name, 'rb').read(), 'html', 'utf-8')
        attach_file.replace_header("Content-Type", "application/octet-stream; name=\"%s\"" % Header(os.path.basename(file_name),"gb2312"))
        attach_file.add_header("Content-Disposition", "attachment;filename=\"%s\"" % Header(os.path.basename(file_name),"gb2312"))
        # attach_file["Content-Type"] = "application/octet-stream"
        # attach_file["Content-Disposition"] = "attachment; filename=/"%s/"" % (os.path.basename(file_name))
        mail.attach(attach_file)

    # 发送邮件
    receiver_list = receivers.split(";")
    try:
        smtp_client = smtplib.SMTP()
        smtp_client.connect(smtp_server, "25")
        smtp_client.login(sender_address, sender_passwd)
        smtp_client.sendmail(sender_address, receiver_list, mail.as_string())
        smtp_client.quit()
        return 0
    except Exception as e:
        print "fail to send the mail: %s" % (e)
        return 1


if __name__ == "__main__":
    init("monitor@ibenben.com", "Fh6oK3QU")
    subject = "腾讯企业邮箱邮件发送测试"
    result = send_email(subject, "hello world", ["../logs/test/logger.log"], "ybzhan@ibenben.com")

    if result == 0:
        print "send the mail successfully"
    else:
        print "fail to send the mail"

