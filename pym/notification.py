import smtplib

# Here are the email package modules we'll need
#from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
# For guessing MIME type based on file name extension
import mimetypes

# Much of this module is copied from 
# http://docs.python.org/library/email-examples.html

COMMASPACE = ', '
# SMTP Server
SMTP_SERVER = 'smtp.gmail.com:587'
from_addr = 'pouyou.fr@gmail.com'
# Who should receive the notifications
to_addrs  = 'boris.chazalet@gmail.com'

# Credentials (if needed)  
username = 'pouyou.fr@gmail.com'  
password = ''  

class Notification(object):

	def __init__(self, text, file_to_attach):
		self.test_mode = False
		# Create the container (outer) email message.
		self.message = MIMEMultipart()
		self.message['Subject'] = "Auto_form report"
		self.message['From'] = from_addr
		self.message['To'] = to_addrs # COMMASPACE.join(family)
		self.message.preamble = 'This is an automatic mail from auto_form'
		self.message.attach(MIMEText(text)) #Body
		if file_to_attach != None:
			ctype, encoding = mimetypes.guess_type(file_to_attach)
			if ctype is None or encoding is not None:
    	        # No guess could be made, or the file is encoded (compressed), so  use a generic bag-of-bits type.
				ctype = 'application/octet-stream'
			maintype, subtype = ctype.split('/', 1)
			if maintype == 'text':
				fp = open(file_to_attach)
				report = MIMEText(fp.read(), _subtype=subtype, _charset="utf-8")
				fp.close()
				# Set the filename parameter
				report.add_header('Content-Disposition', 'attachment', filename="report.csv")
				self.message.attach(report)
			else:
				print "Error sending report. Not a text file."

	def send(self):
		if not self.test_mode:		
			# The actual mail send  
			server = smtplib.SMTP(SMTP_SERVER)
			server.starttls()
			server.login(username,password)  
			server.sendmail(from_addr, to_addrs, self.message.as_string())  
			server.quit()

		#print "Notification sent"

  

