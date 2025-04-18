import mysql.connector
from mysql.connector import Error
import json
from decimal import Decimal

# Custom JSON encoder to handle Decimal types
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

# Database connection configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',  # Update with your MySQL username
    'password': '',  # Update with your MySQL password
    'database': 'artgallery'
}

def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
    return None

# Helper function to safely encode JSON with Decimal values
def json_dumps(data):
    """Safely convert data to JSON string, handling Decimal types"""
    return json.dumps(data, cls=DecimalEncoder)

def dict_from_row(row, cursor):
    """Convert a database row to a dictionary"""
    result = {cursor.column_names[i]: value for i, value in enumerate(row)}
    # Convert Decimal objects to float for JSON serialization
    for key, value in result.items():
        if isinstance(value, Decimal):
            result[key] = float(value)
    return result

# Contact message functions
def save_contact_message(name, email, phone, message, source='contact_form'):
    """Save a new contact message"""
    connection = get_db_connection()
    if connection is None:
        return {"error": "Database connection failed"}
    
    try:
        cursor = connection.cursor()
        
        # Check if contact_messages table has source column
        cursor.execute("SHOW COLUMNS FROM contact_messages LIKE 'source'")
        source_exists = cursor.fetchone()
        
        if not source_exists:
            # Add source column if it doesn't exist
            cursor.execute("ALTER TABLE contact_messages ADD COLUMN source VARCHAR(50) DEFAULT 'contact_form'")
        
        # Insert the message into the database
        query = """
        INSERT INTO contact_messages (name, email, phone, message, source)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (name, email, phone, message, source))
        connection.commit()
        
        return {"success": True, "message_id": cursor.lastrowid}
    
    except Error as e:
        print(f"Error saving contact message: {e}")
        return {"error": str(e)}
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_all_contact_messages():
    """Get all contact messages"""
    connection = get_db_connection()
    if connection is None:
        return {"error": "Database connection failed"}
    
    try:
        cursor = connection.cursor()
        
        # Get all messages ordered by date (newest first)
        query = """
        SELECT * FROM contact_messages
        ORDER BY date DESC
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        
        messages = []
        for row in rows:
            messages.append(dict_from_row(row, cursor))
        
        return {"messages": messages}
    
    except Error as e:
        print(f"Error getting contact messages: {e}")
        return {"error": str(e)}
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def update_message_status(message_id, status):
    """Update the status of a message"""
    connection = get_db_connection()
    if connection is None:
        return {"error": "Database connection failed"}
    
    try:
        cursor = connection.cursor()
        
        # Update the message status
        query = """
        UPDATE contact_messages
        SET status = %s
        WHERE id = %s
        """
        cursor.execute(query, (status, message_id))
        connection.commit()
        
        if cursor.rowcount == 0:
            return {"error": "Message not found"}
        
        return {"success": True}
    
    except Error as e:
        print(f"Error updating message status: {e}")
        return {"error": str(e)}
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
