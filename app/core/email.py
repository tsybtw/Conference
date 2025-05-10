import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string
from typing import Dict

from app.config import settings
from app.core.logging import logger

# Dictionary to store reset codes with email as key
reset_codes: Dict[str, str] = {}

def generate_reset_code(email: str) -> str:
    """Generate a 6-digit reset code and store it for the email"""
    code = ''.join(random.choices(string.digits, k=6))
    reset_codes[email] = code
    return code

def verify_reset_code(email: str, code: str) -> bool:
    """Verify if the reset code for the email is correct"""
    stored_code = reset_codes.get(email)
    if not stored_code:
        return False
    
    # One-time use: remove the code after verification
    if stored_code == code:
        del reset_codes[email]
        return True
    
    return False

def send_email(to_email: str, subject: str, html_content: str) -> bool:
    """Send an email with the given subject and HTML content"""
    if not settings.EMAIL_USERNAME or not settings.EMAIL_PASSWORD:
        logger.error("Email credentials not configured")
        return False
    
    try:
        message = MIMEMultipart()
        message["From"] = settings.EMAIL_FROM
        message["To"] = to_email
        message["Subject"] = subject
        
        message.attach(MIMEText(html_content, "html"))
        
        with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
            if settings.EMAIL_USE_TLS:
                server.starttls()
            
            try:
                server.login(settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD)
            except smtplib.SMTPAuthenticationError as auth_err:
                logger.error(f"SMTP Authentication failed: {str(auth_err)}")
                return False
            except Exception as login_err:
                logger.error(f"SMTP Login error: {str(login_err)}")
                return False
                
            try:
                server.send_message(message)
            except smtplib.SMTPRecipientsRefused:
                logger.error(f"Email recipient refused: {to_email}")
                return False
            except smtplib.SMTPSenderRefused:
                logger.error(f"Email sender refused: {settings.EMAIL_FROM}")
                return False
            except Exception as send_err:
                logger.error(f"Failed to send email: {str(send_err)}")
                return False
        
        logger.info(f"Email sent successfully to {to_email}")
        return True
    
    except smtplib.SMTPConnectError:
        logger.error(f"Failed to connect to SMTP server: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
        return False
    except smtplib.SMTPServerDisconnected:
        logger.error("Server disconnected unexpectedly")
        return False
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return False

def send_password_reset_email(email: str) -> bool:
    """Send a password reset email with a verification code"""
    reset_code = generate_reset_code(email)
    
    subject = f"{settings.APP_NAME} - Password Reset"
    
    html_content = f"""
    <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>We received a request to reset your password for {settings.APP_NAME}.</p>
            <p>Your verification code is: <strong>{reset_code}</strong></p>
            <p>This code will expire in {settings.RESET_TOKEN_EXPIRE_MINUTES} minutes.</p>
            <p>If you did not request a password reset, please ignore this email.</p>
            <p>Best regards,<br>The {settings.APP_NAME} Team</p>
        </body>
    </html>
    """
    
    return send_email(email, subject, html_content) 