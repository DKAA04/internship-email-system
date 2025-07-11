import os
import logging
from typing import List, Tuple, Dict
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "passwd": os.getenv("DB_PASS", ""),
    "database": os.getenv("DB_NAME", "internship"),
}


def connect_to_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            logging.info("Database connection successful.")
        return conn
    except Error as e:
        logging.error(f"Error connecting to MySQL: {e}")
        raise


def search_products(cursor, search_term: str) -> List[Tuple]:
    query = """
        (SELECT * FROM products WHERE Product LIKE %s)
        UNION
        (SELECT * FROM products WHERE Product LIKE %s)
        UNION
        (SELECT * FROM products WHERE Product LIKE %s)
    """
    patterns = (search_term + '%', '%' + search_term, '%' + search_term + '%')
    cursor.execute(query, patterns)
    return cursor.fetchall()


def get_clients_by_companies(cursor, company_names: List[str]) -> List[Tuple]:
    if not company_names:
        return []

    placeholders = ", ".join(["%s"] * len(company_names))
    query = f"SELECT * FROM clients WHERE Company IN ({placeholders})"
    cursor.execute(query, company_names)
    return cursor.fetchall()


def display_results(products: List[Tuple]) -> Dict[str, List]:
    result_map = {}
    for index, item in enumerate(products):
        key = f"row_{index + 1}"
        result_map[key] = list(item)
        print(f"{key}: {item}")
    return result_map


def main():
    conn = connect_to_db()
    cursor = conn.cursor()

    while True:
        search_term = input("Enter the product search term: ").strip()
        if not search_term:
            print("Please enter a valid term.")
            continue

        products = search_products(cursor, search_term)

        if not products:
            print("No items found, try again.")
            continue

        row_map = display_results(products)

        companies = [row[4] for row in row_map.values() if len(row) > 4]
        clients = get_clients_by_companies(cursor, companies)

        if clients:
            print("\n--- Subcontractors Found ---")
            for client in clients:
                print("Subcontractor:", client)

        choice = input("\nType 'ciao' to quit or press Enter to continue: ").strip().lower()
        if choice == 'ciao':
            break

    cursor.close()
    conn.close()
    logging.info("Program terminated successfully.")


if __name__ == "__main__":
    main()
