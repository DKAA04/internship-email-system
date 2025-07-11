import os
import logging
import boto3
import mysql.connector
from typing import List, Dict
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

# Load .env config
load_dotenv()

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Config
AWS_REGION = os.getenv("AWS_REGION")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")

ATTACHMENTS_FOLDER = os.path.abspath('./internshipattachmentsAAWS')

MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST"),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE")
}


def get_mysql_connection():
    return mysql.connector.connect(**MYSQL_CONFIG)


def execute_query(query: str, params=()) -> List[Dict]:
    try:
        with get_mysql_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(query, params)
                if query.lower().startswith("select"):
                    return cursor.fetchall()
                conn.commit()
    except mysql.connector.Error as db_err:
        logging.error(f"MySQL error while executing query: {db_err}")
        raise
    except Exception as ex:
        logging.error(f"Unexpected error in execute_query(): {ex}")
        raise



def update_requests_from_clients_products():
    query = """
    INSERT INTO requests (Company, Email, Registration, ProductRequested, LastEmailSent, Status)
    SELECT 
        c.Company, c.Email, c.Registration, p.Product, c.LastEmailSent, 'Not Responded'
    FROM clients c
    JOIN products p ON c.Company = p.Company
    ON DUPLICATE KEY UPDATE
        LastEmailSent = VALUES(LastEmailSent),
        Status = VALUES(Status);
    """
    try:
        execute_query(query)
        logging.info("Requests table updated successfully.")
    except Exception as e:
        logging.error(f"Failed to update requests: {e}")


def send_email(recipient_email: str, subject: str, body: str, attachments: List[str] = None):
    ses = boto3.client(
        'ses',
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )

    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    if attachments:
        for file in attachments:
            path = os.path.join(ATTACHMENTS_FOLDER, file.strip())
            if not os.path.isfile(path):
                logging.warning(f"Attachment not found: {file}")
                continue

            with open(path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(path)}')
                msg.attach(part)

    import time
    MAX_RETRIES = 3

    for attempt in range(MAX_RETRIES):
        try:
            ses.send_raw_email(
                Source=EMAIL_SENDER,
                Destinations=[recipient_email],
                RawMessage={'Data': msg.as_string()}
            )
            logging.info(f"Email sent to {recipient_email} on attempt {attempt + 1}")
            break
        except Exception as e:
            logging.warning(f"Attempt {attempt + 1} failed for {recipient_email}: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                logging.error(f"Final failure sending email to {recipient_email}: {e}")


