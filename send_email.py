import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
# Load all the secrets for sending the email
load_dotenv()


# Function to send an email
def send_email(recipient_email: str, subject: str, query_answer: str) -> bool:
    """Send email using SMTP."""
    try:
        # Create message
        msg = MIMEMultipart()
        msg["From"] = os.getenv("SENDER_EMAIL")
        msg["To"] = recipient_email
        msg["Subject"] = subject

        # Create email body
        body = f"""
        Here's the answer to your query:

        {query_answer}

        Best regards,
        Vinayak Nayak.
        """

        msg.attach(MIMEText(body, "plain"))

        # Create SMTP session
        server = smtplib.SMTP(os.getenv("SMTP_SERVER"), os.getenv("SMTP_PORT"))
        server.starttls()
        server.login(os.getenv("SENDER_EMAIL"), os.getenv("SENDER_PASSWORD"))

        # Send email
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False
