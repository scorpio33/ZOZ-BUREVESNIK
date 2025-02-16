import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.settings import SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD

class EmailSender:
    def __init__(self):
        self.server = SMTP_SERVER
        self.port = SMTP_PORT
        self.user = SMTP_USER
        self.password = SMTP_PASSWORD
        
    def send_verification_code(self, email: str, code: str) -> bool:
        """Отправка кода подтверждения на email"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.user
            msg['To'] = email
            msg['Subject'] = "Код подтверждения"
            
            body = f"""
            Здравствуйте!
            
            Ваш код подтверждения: {code}
            
            Если вы не запрашивали код, проигнорируйте это сообщение.
            
            С уважением,
            Команда поисково-спасательного бота
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.server, self.port)
            server.starttls()
            server.login(self.user, self.password)
            server.send_message(msg)
            server.quit()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False