# database.py

import sqlite3
import os
import json

DB_FILE = "data.db"


def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
    except sqlite3.Error as e:
        print(e)
    return conn


def create_tables():
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            # UPDATED SCHEMA: Replaced single 'address' with structured fields
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS companies (
                    name TEXT PRIMARY KEY,
                    address_1 TEXT,
                    address_2 TEXT,
                    address_3 TEXT,
                    city TEXT,
                    postcode TEXT,
                    state TEXT,
                    phone TEXT,
                    old_roc TEXT,
                    new_roc TEXT
                );
            """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS insurance_companies (
                    name TEXT PRIMARY KEY,
                    address_1 TEXT,
                    address_2 TEXT,
                    address_3 TEXT,
                    city TEXT,
                    postcode TEXT,
                    state TEXT,
                    phone TEXT,
                    old_roc TEXT,
                    new_roc TEXT
                );
            """
            )
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")
        finally:
            conn.close()


# UPDATED FUNCTION: New parameters for structured address
def add_company(
    name,
    address_1,
    address_2,
    address_3,
    city,
    postcode,
    state,
    phone,
    old_roc,
    new_roc,
):
    conn = create_connection()
    sql = """ INSERT OR REPLACE INTO companies(name, address_1, address_2, address_3, city, postcode, state, phone, old_roc, new_roc)
              VALUES(?,?,?,?,?,?,?,?,?,?) """
    try:
        cursor = conn.cursor()
        cursor.execute(
            sql,
            (
                name,
                address_1,
                address_2,
                address_3,
                city,
                postcode,
                state,
                phone,
                old_roc,
                new_roc,
            ),
        )
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error adding company: {e}")
    finally:
        if conn:
            conn.close()


def add_insurance_company(
    name,
    address_1,
    address_2,
    address_3,
    city,
    postcode,
    state,
    phone,
    old_roc,
    new_roc,
):
    conn = create_connection()
    sql = """ INSERT OR REPLACE INTO insurance_companies(name, address_1, address_2, address_3, city, postcode, state, phone, old_roc, new_roc)
              VALUES(?,?,?,?,?,?,?,?,?,?) """
    try:
        cursor = conn.cursor()
        cursor.execute(
            sql,
            (
                name,
                address_1,
                address_2,
                address_3,
                city,
                postcode,
                state,
                phone,
                old_roc,
                new_roc,
            ),
        )
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error adding insurance company: {e}")
    finally:
        if conn:
            conn.close()


# All 'get' functions now return a dictionary with the new address fields
def get_company_by_name(name):
    conn = create_connection()
    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM companies WHERE name=?", (name,))
        row = cursor.fetchone()
        if row:
            return dict(row)
    except sqlite3.Error as e:
        print(f"Error getting company: {e}")
    finally:
        if conn:
            conn.close()
    return None


def get_insurance_company_by_name(name):
    conn = create_connection()
    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM insurance_companies WHERE name=?", (name,))
        row = cursor.fetchone()
        if row:
            return dict(row)
    except sqlite3.Error as e:
        print(f"Error getting insurance company: {e}")
    finally:
        if conn:
            conn.close()
    return None


def get_all_company_names():
    conn = create_connection()
    names = []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM companies ORDER BY name")
        rows = cursor.fetchall()
        names = [row[0] for row in rows]
    except sqlite3.Error as e:
        print(f"Error getting company names: {e}")
    finally:
        if conn:
            conn.close()
    return names


def get_all_insurance_company_names():
    conn = create_connection()
    names = []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM insurance_companies ORDER BY name")
        rows = cursor.fetchall()
        names = [row[0] for row in rows]
    except sqlite3.Error as e:
        print(f"Error getting insurance company names: {e}")
    finally:
        if conn:
            conn.close()
    return names


def delete_company(name):
    conn = create_connection()
    sql = "DELETE FROM companies WHERE name=?"
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (name,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error deleting company: {e}")
    finally:
        if conn:
            conn.close()


def delete_insurance_company(name):
    conn = create_connection()
    sql = "DELETE FROM insurance_companies WHERE name=?"
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (name,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error deleting insurance company: {e}")
    finally:
        if conn:
            conn.close()


# UPDATED: Now inserts the Zurich data into the new structured fields
def add_default_insurance_if_empty():
    conn = create_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM insurance_companies")
        count = cursor.fetchone()[0]
        if count == 0:
            print("Insurance company table is empty. Adding default Zurich data.")
            # Based on the data you provided for Zurich
            add_insurance_company(
                name="Zurich General Insurance Malaysia Berhad",
                address_1="LEVEL 23A, MERCU 3,",
                address_2="NO. 3, JALAN BANGSAR,",
                address_3="KL ECO CITY,",
                city="KUALA LUMPUR",
                postcode="59200",
                state="Wilayah Persekutuan Kuala Lumpur",  # Using the full name from the dropdown
                phone="0321096000",
                old_roc="1249516V",
                new_roc="201701035345",
            )
    except sqlite3.Error as e:
        print(f"Error checking/adding default insurance data: {e}")
    finally:
        if conn:
            conn.close()


def is_company_table_empty():
    """Checks if the main 'companies' table has any records."""
    conn = create_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM companies")
        count = cursor.fetchone()[0]
        return count == 0
    except sqlite3.Error:
        return True  # Assume empty on error
    finally:
        if conn:
            conn.close()


def is_insurance_table_empty():
    """Checks if the 'insurance_companies' table has any records."""
    conn = create_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM insurance_companies")
        count = cursor.fetchone()[0]
        return count == 0
    except sqlite3.Error:
        return True
    finally:
        if conn:
            conn.close()


def preload_initial_companies():
    """Loads company data from initial_companies.json into the database."""
    json_file = "initial_data/initial_companies.json"
    if not os.path.exists(json_file):
        print(f"'{json_file}' not found. Skipping company preloading.")
        return

    print("Preloading initial company data from JSON...")
    with open(json_file, "r") as f:
        companies = json.load(f)

    for company_data in companies:
        print(f"  -> Loading data for {company_data['name']}")
        add_company(
            name=company_data.get("name"),
            old_roc=company_data.get("old_roc"),
            new_roc=company_data.get("new_roc"),
            address_1=company_data.get("address_1"),
            address_2=company_data.get("address_2"),
            address_3=company_data.get("address_3"),
            city=company_data.get("city"),
            postcode=company_data.get("postcode"),
            state=company_data.get("state"),
            phone=company_data.get("phone"),
        )
    print("Company data preloading complete.")


def preload_initial_insurance():
    """Loads insurance data from initial_insurance.json into the database."""
    json_file = "initial_data/initial_insurance.json"
    if not os.path.exists(json_file):
        print(f"'{json_file}' not found. Skipping insurance preloading.")
        return

    print("Preloading initial insurance data from JSON...")
    with open(json_file, "r") as f:
        insurances = json.load(f)

    for insurance_data in insurances:
        print(f"  -> Loading data for {insurance_data['name']}")
        add_insurance_company(
            name=insurance_data.get("name"),
            old_roc=insurance_data.get("old_roc"),
            new_roc=insurance_data.get("new_roc"),
            address_1=insurance_data.get("address_1"),
            address_2=insurance_data.get("address_2"),
            address_3=insurance_data.get("address_3"),
            city=insurance_data.get("city"),
            postcode=insurance_data.get("postcode"),
            state=insurance_data.get("state"),
            phone=insurance_data.get("phone"),
        )
    print("Insurance data preloading complete.")
