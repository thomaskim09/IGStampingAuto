import sqlite3

DB_FILE = "data.db"


def create_connection():
    """Create a database connection to the SQLite database."""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
    except sqlite3.Error as e:
        print(e)
    return conn


def create_tables():
    """Create the necessary tables if they don't exist."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            # Table for main companies
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS companies (
                    name TEXT PRIMARY KEY,
                    address TEXT,
                    old_roc TEXT,
                    new_roc TEXT,
                    phone TEXT
                );
            """
            )
            # Table for insurance companies
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS insurance_companies (
                    name TEXT PRIMARY KEY,
                    address TEXT,
                    old_roc TEXT,
                    new_roc TEXT,
                    phone TEXT
                );
            """
            )
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")
        finally:
            conn.close()


def add_company(name, address, old_roc, new_roc, phone):
    """Add or update a company in the database."""
    conn = create_connection()
    sql = """ INSERT OR REPLACE INTO companies(name, address, old_roc, new_roc, phone)
              VALUES(?,?,?,?,?) """
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (name, address, old_roc, new_roc, phone))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error adding company: {e}")
    finally:
        if conn:
            conn.close()


def add_insurance_company(name, address, old_roc, new_roc, phone):
    """Add or update an insurance company in the database."""
    conn = create_connection()
    sql = """ INSERT OR REPLACE INTO insurance_companies(name, address, old_roc, new_roc, phone)
              VALUES(?,?,?,?,?) """
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (name, address, old_roc, new_roc, phone))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error adding insurance company: {e}")
    finally:
        if conn:
            conn.close()


def get_company_by_name(name):
    """Query a company by name."""
    conn = create_connection()
    try:
        conn.row_factory = sqlite3.Row  # Allows accessing columns by name
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM companies WHERE name=?", (name,))
        row = cursor.fetchone()
        if row:
            return dict(row)  # Return as a dictionary
    except sqlite3.Error as e:
        print(f"Error getting company: {e}")
    finally:
        if conn:
            conn.close()
    return None


def get_insurance_company_by_name(name):
    """Query an insurance company by name."""
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
    """Retrieve all company names."""
    conn = create_connection()
    names = []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM companies ORDER BY name")
        rows = cursor.fetchall()
        # rows will be a list of tuples, e.g., [('Company A',), ('Company B',)]
        # We convert it to a simple list: ['Company A', 'Company B']
        names = [row[0] for row in rows]
    except sqlite3.Error as e:
        print(f"Error getting company names: {e}")
    finally:
        if conn:
            conn.close()
    return names


def get_all_insurance_company_names():
    """Retrieve all insurance company names."""
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
    """Delete a company from the database by name."""
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
    """Delete an insurance company from the database by name."""
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


def add_default_insurance_if_empty():
    """
    Checks if the insurance_companies table is empty and, if so,
    adds the default Zurich General Insurance data.
    """
    conn = create_connection()
    try:
        cursor = conn.cursor()
        # Check if any records exist
        cursor.execute("SELECT COUNT(*) FROM insurance_companies")
        count = cursor.fetchone()[0]

        # If no records exist, add the default one
        if count == 0:
            print("Insurance company table is empty. Adding default Zurich data.")
            default_data = {
                "name": "Zurich General Insurance Malaysia Berhad",
                "address": "Level 23A, Mercu 3, No. 3, Jalan Bangsar, KL Eco City, 59200 Kuala Lumpur, Malaysia",
                "new_roc": "201701035345",
                "old_roc": "1249516-V",
                "phone": "03-2109 6000",
            }
            # Use the existing add function to insert the data
            add_insurance_company(
                default_data["name"],
                default_data["address"],
                default_data["old_roc"],
                default_data["new_roc"],
                default_data["phone"],
            )
    except sqlite3.Error as e:
        print(f"Error checking/adding default insurance data: {e}")
    finally:
        if conn:
            conn.close()
