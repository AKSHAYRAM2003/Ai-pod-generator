import smtplib
import ssl
import secrets
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from typing import Optional
from datetime import datetime

from app.core.config import settings
from app.core.exceptions import AppException


logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails with Gmail SMTP and verification codes"""
    
    def __init__(self):
        # Gmail SMTP configuration from environment variables
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM_EMAIL
        self.from_name = settings.SMTP_FROM_NAME
        self.frontend_url = settings.FRONTEND_URL
    
    def generate_verification_code(self) -> str:
        """Generate 6-digit verification code"""
        return f"{secrets.randbelow(900000) + 100000}"
    
    async def send_verification_code_email(self, email: str, first_name: str, verification_code: str):
        """Send 6-digit verification code via email"""
        
        subject = "🎧 Your AiPod Verification Code"
        
        html_content = self._get_verification_code_html_template(first_name, verification_code)
        text_content = self._get_verification_code_text_template(first_name, verification_code)
        
        await self._send_via_gmail_smtp(email, subject, html_content, text_content)
        
        # Log for development
        logger.info(f"📧 Verification code sent to {email}: {verification_code}")
    
    async def send_password_reset_code_email(self, email: str, first_name: str, reset_code: str):
        """Send 6-digit password reset code via email"""
        
        subject = "🔒 Your AiPod Password Reset Code"
        
        html_content = self._get_password_reset_code_html_template(first_name, reset_code)
        text_content = self._get_password_reset_code_text_template(first_name, reset_code)
        
        await self._send_via_gmail_smtp(email, subject, html_content, text_content)
        
        # Log for development
        logger.info(f"🔒 Password reset code sent to {email}: {reset_code}")
    
    async def send_welcome_email(self, email: str, first_name: str):
        """Send welcome email after successful verification"""
        
        subject = "🎉 Welcome to AiPod - You're All Set!"
        
        html_content = self._get_welcome_html_template(first_name)
        text_content = self._get_welcome_text_template(first_name)
        
        await self._send_via_gmail_smtp(email, subject, html_content, text_content)
        
        logger.info(f"🎉 Welcome email sent to {email}")
    
    async def _send_via_gmail_smtp(self, email: str, subject: str, html_content: str, text_content: str):
        """Send email via Gmail SMTP"""
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = email
            msg['Reply-To'] = self.from_email
            
            # Add both text and HTML versions
            text_part = MIMEText(text_content, 'plain', 'utf-8')
            html_part = MIMEText(html_content, 'html', 'utf-8')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email via Gmail SMTP
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"📧 Email sent successfully to: {email}")
            
        except Exception as e:
            logger.error(f"❌ Gmail SMTP sending failed: {str(e)}")
            # Fallback to console logging for development
            self._log_email_to_console(email, subject, html_content)
            raise AppException(f"Failed to send email: {str(e)}", status_code=500, error_code="EMAIL_SEND_FAILED")
    
    def _log_email_to_console(self, email: str, subject: str, content: str):
        """Log email to console when Gmail is not available (development fallback)"""
        print("\n" + "="*80)
        print("📧 EMAIL SENT VIA GMAIL SMTP")
        print("="*80)
        print(f"To: {email}")
        print(f"Subject: {subject}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("-" * 80)
        # Extract verification code from content for easy testing
        import re
        code_match = re.search(r'\b\d{6}\b', content)
        if code_match:
            print(f"🔢 VERIFICATION CODE: {code_match.group()}")
        print("="*80 + "\n")
    
    def _get_verification_code_html_template(self, first_name: str, verification_code: str) -> str:
        """HTML template for 6-digit verification code"""
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Your AiPod Verification Code</title>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; 
                    line-height: 1.6; 
                    color: #333333; 
                    background-color: #f8f9fa; 
                }}
                .container {{ 
                    max-width: 600px; 
                    margin: 0 auto; 
                    background: #ffffff; 
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    border-radius: 8px;
                    overflow: hidden;
                }}
                .header {{ 
                    background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%); 
                    color: #ffffff; 
                    padding: 40px 30px; 
                    text-align: center; 
                }}
                .logo {{ 
                    font-size: 36px; 
                    font-weight: bold; 
                    margin-bottom: 10px;
                }}
                .content {{ 
                    padding: 40px 30px; 
                    text-align: center;
                }}
                .welcome-message {{ 
                    font-size: 24px; 
                    font-weight: 600; 
                    margin-bottom: 20px; 
                    color: #1a1a1a;
                }}
                .verification-code-section {{ 
                    background: #f8f9fa; 
                    padding: 40px 30px; 
                    margin: 30px 0; 
                    border-radius: 12px; 
                    border: 2px dashed #1DB954;
                }}
                .verification-code {{ 
                    font-size: 48px; 
                    font-weight: bold; 
                    color: #1DB954; 
                    letter-spacing: 8px; 
                    margin: 20px 0; 
                    font-family: 'Courier New', monospace;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
                }}
                .expiry-notice {{ 
                    background: #fff3cd; 
                    border: 1px solid #ffeaa7; 
                    border-radius: 6px; 
                    padding: 15px; 
                    margin: 25px 0; 
                    font-size: 14px; 
                    color: #856404;
                }}
                .footer {{ 
                    background: #f8f9fa; 
                    padding: 30px; 
                    text-align: center; 
                    border-top: 1px solid #e9ecef;
                    color: #666666; 
                    font-size: 14px;
                }}
                @media only screen and (max-width: 600px) {{
                    .verification-code {{ font-size: 36px; letter-spacing: 4px; }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🎧 AiPod</div>
                    <div style="font-size: 16px; opacity: 0.9; margin-top: 8px;">
                        AI-Powered Podcast Generation
                    </div>
                </div>
                
                <div class="content">
                    <div class="welcome-message">Welcome, {first_name}! 👋</div>
                    
                    <p style="font-size: 16px; margin-bottom: 30px; color: #555;">
                        Thank you for joining AiPod! To complete your registration and start creating 
                        amazing AI-powered podcasts, please enter this verification code:
                    </p>
                    
                    <div class="verification-code-section">
                        <div style="font-size: 16px; color: #666; margin-bottom: 15px;">
                            <strong>Your Verification Code:</strong>
                        </div>
                        <div class="verification-code">{verification_code}</div>
                        <div style="font-size: 14px; color: #666; margin-top: 15px;">
                            Enter this code in the verification page to activate your account
                        </div>
                    </div>
                    
                    <div class="expiry-notice">
                        <strong>🔒 Security Notice:</strong> This code expires in <strong>10 minutes</strong> 
                        and can only be used once. Never share this code with anyone.
                    </div>
                    
                    <div style="margin-top: 30px; padding: 20px; background: #f1f3f4; border-radius: 8px; font-size: 14px; color: #666;">
                        <strong>Need help?</strong> If you didn't create an AiPod account, you can safely ignore this email.
                        <br><br>
                        Questions? Reply to this email and we'll help you out!
                    </div>
                </div>
                
                <div class="footer">
                    <div style="font-weight: 600; margin-bottom: 15px;">
                        Welcome to the Future of Podcasting! 🚀
                    </div>
                    
                    <div style="margin-top: 20px; color: #999;">
                        © 2024 AiPod. All rights reserved.<br>
                        Made with ❤️ for podcast creators worldwide
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_verification_code_text_template(self, first_name: str, verification_code: str) -> str:
        """Text version for verification code email"""
        return f"""🎧 AiPod - Verification Code
        
Hi {first_name}!

Welcome to AiPod - AI-Powered Podcast Generation!

Your verification code is: {verification_code}

🔒 This code expires in 10 minutes and can only be used once.

Enter this code in the verification page to activate your account and start creating amazing AI-powered podcasts!

If you didn't create an AiPod account, please ignore this email.

Questions? Reply to this email and we'll help you out!

Welcome to the future of podcasting! 🚀

© 2024 AiPod. All rights reserved."""
    
    def _get_password_reset_code_html_template(self, first_name: str, reset_code: str) -> str:
        """HTML template for password reset code"""
        return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Password Reset Code</title></head>
<body style="font-family: Arial, sans-serif; background: #f8f9fa; margin: 0; padding: 20px;">
    <div style="max-width: 600px; margin: 0 auto; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <div style="background: linear-gradient(135deg, #dc3545 0%, #c82333 100%); color: #fff; padding: 40px; text-align: center;">
            <h1 style="margin: 0; font-size: 36px;">🔒 Password Reset</h1>
            <p style="margin: 10px 0 0; opacity: 0.9;">AiPod Account Security</p>
        </div>
        <div style="padding: 40px; text-align: center;">
            <h2>Hi {first_name},</h2>
            <p>We received a request to reset your AiPod account password. Use this verification code:</p>
            <div style="background: #f8f9fa; padding: 30px; margin: 20px 0; border-radius: 12px; border: 2px dashed #dc3545;">
                <div style="font-size: 48px; font-weight: bold; color: #dc3545; letter-spacing: 8px; font-family: monospace;">{reset_code}</div>
            </div>
            <div style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 6px; margin: 20px 0; color: #856404;">
                <strong>⏰ Security Notice:</strong> This code expires in 10 minutes.
            </div>
        </div>
    </div>
</body></html>"""
    
    def _get_password_reset_code_text_template(self, first_name: str, reset_code: str) -> str:
        """Text version for password reset code"""
        return f"""🔒 Password Reset Code - AiPod

Hi {first_name},

We received a request to reset your AiPod account password.

Your password reset code: {reset_code}

⏰ This code expires in 10 minutes and can only be used once.

If you didn't request this reset, please ignore this email."""
    
    def _get_welcome_html_template(self, first_name: str) -> str:
        """Welcome email after successful verification"""
        return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Welcome to AiPod!</title></head>
<body style="font-family: Arial, sans-serif; background: #f8f9fa; margin: 0; padding: 20px;">
    <div style="max-width: 600px; margin: 0 auto; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <div style="background: linear-gradient(135deg, #1DB954 0%, #1ed760 100%); color: #fff; padding: 40px; text-align: center;">
            <h1 style="margin: 0; font-size: 36px;">🎉 Welcome to AiPod!</h1>
            <p style="margin: 10px 0 0; opacity: 0.9;">You're officially part of the community!</p>
        </div>
        <div style="padding: 40px;">
            <h2>Congratulations, {first_name}! 🚀</h2>
            <p>Your email has been verified and your AiPod account is now fully activated! You can now access all features and start creating amazing AI-powered podcasts.</p>
            <div style="text-align: center; margin: 35px 0;">
                <a href="{self.frontend_url}/dashboard" style="background: #1DB954; color: #fff; padding: 16px 32px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">
                    🚀 Start Creating Your First Podcast
                </a>
            </div>
        </div>
    </div>
</body></html>"""
    
    def _get_welcome_text_template(self, first_name: str) -> str:
        """Text version of welcome email"""
        return f"""🎉 Welcome to AiPod, {first_name}!

Congratulations! Your email has been verified and your AiPod account is fully activated.

You can now start creating amazing AI-powered podcasts!

Visit: {self.frontend_url}/dashboard

Welcome to the AiPod community! 🎧

© 2024 AiPod"""


# Create singleton instance
email_service = EmailService()
