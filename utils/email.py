import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
    

 class EmailSender:
    _GMAIL_SMTP_URL = smtp.gmail.com
    _GMAIL_SMTP_PORT = 587


    def __init__(self, source, destination, password, *args, **kwargs)
        self._source = source
        self._destination = destination
        self._password = password

    def __repr__(self):
         return ('{self.__class__.__name__}('
                 f'{self._source!r}, {self._destination!r}, )')
    
    def __str__(self):
        return f'A email sender utility object'

    
    def _create_message(self, subject, body):
        self.message = MIMEMultipart()
        msg['From'] = self._source
        msg['To'] = self._destination
        msg['Subject'] = subject
        body = body

        self.message.attach(MIMEText(body, plain))

    def _send_email(self,smtp_url=self.GMAIL_SMTP_URL, smtp_port=self.GMAIL_SMTP_PORT):
        server = smtplib.SMTP(smtp_url, smtp_port)
        server.login(self._source, self._password)

        msg = self.message.as_string()

        server.sendmail(self._source, self._destination, msg)
        server.quit()


                        

        
