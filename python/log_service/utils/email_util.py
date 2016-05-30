#!/usr/bin/python
#encoding=utf-8

import sys
import os.path
import json

import smtplib
from email.Header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime


smtp_server = 'smtp.exmail.qq.com'

# recv_list: 'xxx@ibenben.com;yyy@ibenben.com'
def send_email(title, file_name, attach_files, recv_list, user_name, passwd):
	with open(file_name, 'r') as f:
		content = f.read()
	
	msg = MIMEMultipart()
	html = MIMEText(content, _subtype='html', _charset='utf-8')
	msg.attach(html)

	# 附件
	for attach_file in attach_files:
		att = MIMEText(open(attach_file, 'rb').read(), 'html', 'utf-8')
		att.replace_header("Content-Type", "application/octet-stream; name=\"%s\"" % Header(os.path.basename(attach_file),"gb2312"))
		att.add_header("Content-Disposition", "attachment;filename=\"%s\"" % Header(os.path.basename(attach_file),"gb2312"))
		
		#att["Content-Type"] = 'application/octet-stream'
		#att["Content-Disposition"] = 'attachment; filename="%s"' % (os.path.basename(attach_file))
		
		msg.attach(att)
	
	email_list = recv_list.split(';')

	msg['Subject'] = title
	msg['From'] = user_name
	msg['To'] = recv_list

	try:
		s = smtplib.SMTP()
		s.connect(smtp_server, '25')
		s.login(user_name, passwd)
		s.sendmail(user_name, email_list, msg.as_string())
		s.quit()
		return 0
	except Exception,e:
		print str(e)
		return 1


if __name__ == '__main__':
	if len(sys.argv) != 2:
		print "invalid usage"
		sys.exit()

	if sys.argv[1] == "pre-release":
		print "pre-release"
		with open("../config/json.conf", 'r') as fd:
			conf = json.load(fd)
			sender = conf["pre-release"]["email"]["sender"]
			passwd = conf["pre-release"]["email"]["password"]
			receiver = conf["pre-release"]["email"]["receiver"]
	elif sys.argv[1] == "production":
		print "production"
		with open("../config/json.conf", 'r') as fd:
			conf = json.load(fd)
			sender = conf["pre-release"]["email"]["sender"]
			passwd = conf["pre-release"]["email"]["password"]
			receiver = conf["pre-release"]["email"]["receiver"]
	else:
		print "invalid parameter"
		sys.exit()
	
	cur_day = datetime.date.today()
	title = '[' + cur_day.strftime('%Y-%m-%d')  + ']' + '腾讯企业邮箱测试邮件'
	print "sender: %s" % (sender)
	print "receiver: %s" % (receiver)
	send_email(title, '../report_archive/helloworld', [], receiver, sender, passwd)
