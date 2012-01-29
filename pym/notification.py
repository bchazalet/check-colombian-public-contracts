import smtplib

# SMTP Server
SMTP_SERVER = 'smtp.gmail.com:587'
from_addr = 'pouyou.fr@gmail.com'
# Who should receive the notifications
to_addrs  = 'boris.chazalet@gmail.com'

# Credentials (if needed)  
username = 'pouyou.fr@gmail.com'  
password = ''  

class Notification(object):

	def __init__(self, subject, msg):
		self.test_mode = True
		self.message = """From: Notification <%s>
		To: <%s>
		Subject: %s
	
		%s.""" % (from_addr,to_addrs, subject, msg)

	def send(self):
		if not self.test_mode:		
			# The actual mail send  
			server = smtplib.SMTP(SMTP_SERVER)
			server.starttls()
			server.login(username,password)  
			server.sendmail(from_addr, to_addrs, self.message)  
			server.quit()

		#print "Notification sent"

  

