# Email and Product Lookup Automation

**Python building blocks for MySQL lookup and AWS SES email delivery.**

This repository contains a command-line product/client lookup tool and a separate email helper module. It is a small automation prototype, not a complete deployed messaging service.

## What is implemented

- Product search and company-based client lookup with parameterized SQL.
- AWS SES raw MIME email delivery with optional file attachments.
- Up to three delivery attempts with exponential backoff.
- A helper to populate request records from client/product tables.
- A mocked email-send unit test.

`main.py` performs interactive database lookup. It does **not** invoke the email sender or automatically deliver messages.

## Setup

```bash
git clone https://github.com/DKAA04/internship-email-system.git
cd internship-email-system
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`.

Create an ignored `.env` with the variables required for the component you use:

```dotenv
# main.py: interactive lookup
DB_HOST=localhost
DB_USER=
DB_PASS=
DB_NAME=

# email_handler.py: database helpers
MYSQL_HOST=localhost
MYSQL_USER=
MYSQL_PASSWORD=
MYSQL_DATABASE=

# email_handler.py: AWS SES
AWS_REGION=
AWS_ACCESS_KEY=
AWS_SECRET_KEY=
EMAIL_SENDER=
```

The two modules currently use different database-variable names. The database schema and seed data are not included; inspect the SQL in each module and provide a synthetic test database with the required `products`, `clients` and `requests` fields before running it.

```bash
python main.py
```

Email delivery is exposed through `email_handler.send_email(...)`. Calling it with configured credentials sends a real message; use controlled test recipients. Attachments are read from `internshipattachmentsAAWS/` relative to the working directory.

## Test without sending email

```bash
python -m unittest discover tests
```

The existing test mocks the SES client and checks that a send is attempted. It does not cover database integration, attachment safety or all retry cases.

## Limitations and publication boundary

- Delivery failures are logged after retries rather than returned as a structured failure result.
- Attachment paths require validation before accepting untrusted filenames.
- Database results and recipient addresses may appear in logs or console output.
- Keep client lists, company database exports, attachments and AWS credentials private. Confirm permission to publish internship-derived code before adding further material.

**Stack:** Python, MySQL Connector, boto3/AWS SES, python-dotenv and unittest.
