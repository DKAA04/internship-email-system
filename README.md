# Internship Email Handler Project

## Overview
Automates email sending using AWS SES with product/client retrieval from MySQL. Includes retries, logging, and modular design.

## Setup

1. Clone the repo
2. Create `.env` file with:
    ```
    AWS_REGION=
    AWS_ACCESS_KEY=
    AWS_SECRET_KEY=
    EMAIL_SENDER=
    MYSQL_HOST=
    MYSQL_USER=
    MYSQL_PASSWORD=
    MYSQL_DATABASE=
    ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Run the app:
    ```bash
    python main.py
    ```

## Features

- Email sending with retry logic
- MySQL integration
- Logging and exception handling
- Unit testable structure

## Test
```bash
python -m unittest discover tests
