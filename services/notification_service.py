from typing import Dict, Any, List, Union
from aop.log.logging_aspect import log_calls
from aop.exception.error_handling_aspect import handle_errors
from logger.get_logger import get_logger

class EmailNotifierService:
    def __init__(self, smtp_config: Dict[str, Any]):
        """
        Initialize the email notifier service.
        
        Args:
            smtp_config (dict): Dictionary containing SMTP configuration
                - host (str): SMTP server address (default: 'smtp.gmail.com')
                - port (int): SMTP server port (default: 587)
                - username (str): Gmail address
                - app_password (str): Gmail app password
                - from_email (str): Sender email address
                - to_emails (list): List of recipient email addresses
        """
        self.smtp_server = smtp_config.get('host', 'smtp.gmail.com')
        self.smtp_port = smtp_config.get('port', 587)
        self.username = smtp_config.get('username', '')
        self.app_password = smtp_config.get('app_password', '')
        self.from_email = smtp_config.get('from_email', self.username)
        self.to_emails = smtp_config.get('recipients', [])
        
        if not all([self.smtp_server, self.username, self.app_password, self.from_email, self.to_emails]):
            logger = get_logger()
            missing_configs = []
            if not self.smtp_server:
                missing_configs.append("smtp_server")
            if not self.username:
                missing_configs.append("username")
            if not self.app_password:
                missing_configs.append("app_password")
            if not self.from_email:
                missing_configs.append("from_email")
            if not self.to_emails:
                missing_configs.append("to_emails")
            
            logger.error(f"Email notifier is not fully configured. Missing: {', '.join(missing_configs)}")
            logger.error(f"Current config - SMTP: {self.smtp_server}, Port: {self.smtp_port}, Username: {self.username}, From: {self.from_email}, Recipients: {self.to_emails}")

    def send_email(self, subject: str, message: str, is_html: bool = False) -> bool:
        """
        Send an email notification.
        
        Args:
            subject (str): Email subject
            message (str): Email body content
            is_html (bool): Whether the message is HTML formatted
            
        Returns:
            bool: True if the email was sent successfully, False otherwise
        """
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        from logger.get_logger import get_logger
        
        logger = get_logger()
        
        if not all([self.smtp_server, self.username, self.app_password, self.from_email, self.to_emails]):
            logger.error("Cannot send email: Email notifier is not properly configured.")
            return False

        try:
            # Test network connectivity first
            import socket
            try:
                socket.create_connection((self.smtp_server, self.smtp_port), timeout=10)
                logger.info(f"Network connectivity to {self.smtp_server}:{self.smtp_port} is available")
            except socket.error as e:
                logger.error(f"Network connectivity test failed: {str(e)}")
                logger.error(f"Cannot reach SMTP server {self.smtp_server}:{self.smtp_port}")
                return False

            # Create message container
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = ', '.join(self.to_emails) if isinstance(self.to_emails, list) else self.to_emails
            msg['Subject'] = f"[Backup Service] {subject}"
            msg['X-Priority'] = '3'
            msg['X-MSMail-Priority'] = 'Normal'
            msg['X-Mailer'] = 'BackupService/1.0'
            
            # Attach the message
            msg.attach(MIMEText(message, 'html' if is_html else 'plain'))

            # Connect to the SMTP server and send the email
            logger.info(f"Attempting to connect to SMTP server {self.smtp_server}:{self.smtp_port}")
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as server:
                server.ehlo()
                server.starttls()
                logger.info(f"Attempting to login with username: {self.username}")
                server.login(self.username, self.app_password)
                logger.info("SMTP login successful, sending email...")
                server.send_message(msg)
                
            logger.info(f"Email notification sent successfully to {msg['To']}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"Failed to authenticate with email server: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Failed to send email notification: {str(e)}")
            return False


class NotificationService:
    def __init__(self, smtp_config: Dict[str, Any], logger_getter):
        """
        Initialize the notification service.
        
        Args:
            smtp_config (dict): SMTP configuration dictionary containing:
                - host: SMTP server host (default: 'smtp.gmail.com')
                - port: SMTP server port (default: 587)
                - username: Email username (Gmail address)
                - app_password: App password for the email account
                - from_email: Sender email address
                - recipients: List of recipient email addresses
            logger_getter: Function to get logger instance
        """
        self._logger_getter = logger_getter
        self.email_notifier = EmailNotifierService(smtp_config)

    @log_calls(lambda self=None: get_logger())
    @handle_errors(lambda self=None: get_logger())
    def send_failure_email(self, subject: str, body: str) -> None:
        """
        Send a failure notification email.
        
        Args:
            subject (str): Email subject
            body (str): Email body content
        """
        # Add some formatting for error messages
        formatted_body = f"""
        <html>
            <body>
                <h2 style="color: #d32f2f;">❌ Backup Failed</h2>
                <p><strong>Error Details:</strong></p>
                <p>{body}</p>
                <hr>
                <p><small>This is an automated message from the Backup Service.</small></p>
            </body>
        </html>
        """
        self.email_notifier.send_email(
            subject=f"❌ {subject}",
            message=formatted_body,
            is_html=True
        )

    @log_calls(lambda self=None: get_logger())
    @handle_errors(lambda self=None: get_logger())
    def send_success_email(self, subject: str, body: str, databases: list = None) -> None:
        """
        Send a success notification email.
        
        Args:
            subject (str): Email subject
            body (str): Email body content
            databases (list, optional): List of database names that were backed up
        """
        # Format the databases list if provided
        databases_section = ""
        if databases:
            db_list = "".join(f"<li>{db}</li>" for db in databases)
            databases_section = f"""
                <h3>Backed Up Databases:</h3>
                <ul>
                    {db_list}
                </ul>
            """

        # Add some formatting for success messages
        formatted_body = f"""
        <html>
            <body>
                <h2 style="color: #388e3c;">✅ Backup Completed Successfully</h2>
                <p>{body}</p>
                {databases_section}
                <hr>
                <p><small>This is an automated message from the Backup Service.</small></p>
            </body>
        </html>
        """
        self.email_notifier.send_email(
            subject=f"✅ {subject}",
            message=formatted_body,
            is_html=True
        )


