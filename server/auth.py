
import hashlib
import secrets
from database import get_db_connection, json_dumps
import jwt
import datetime
from decimal import Decimal
from functools import wraps

# Secret key for JWT token generation - replace with a secure random string
SECRET_KEY = "your_secret_key_replace_this_with_a_secure_random_string"

def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(name, email, password, phone):
    """Register a new user"""
    connection = get_db_connection()
    if connection is None:
        return {"error": "Database connection failed"}
    
    cursor = connection.cursor()
    hashed_password = hash_password(password)
    
    try:
        # Check if email already exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return {"error": "Email already registered"}
        
        # Insert the new user
        query = """
        INSERT INTO users (name, email, password, phone)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (name, email, hashed_password, phone))
        connection.commit()
        
        # Get the new user ID
        user_id = cursor.lastrowid
        
        # Generate token for the new user
        token = generate_token(user_id, name, False)
        
        return {
            "token": token,
            "user_id": user_id,
            "name": name
        }
    except Exception as e:
        print(f"Error registering user: {e}")
        return {"error": str(e)}
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def login_user(email, password):
    """Login a user"""
    connection = get_db_connection()
    if connection is None:
        return {"error": "Database connection failed"}
    
    cursor = connection.cursor()
    hashed_password = hash_password(password)
    
    try:
        # Check user credentials
        query = "SELECT id, name FROM users WHERE email = %s AND password = %s"
        cursor.execute(query, (email, hashed_password))
        user = cursor.fetchone()
        
        if not user:
            return {"error": "Invalid credentials"}
        
        # Generate token for the user
        user_id, name = user
        token = generate_token(user_id, name, False)
        
        return {
            "token": token,
            "user_id": user_id,
            "name": name
        }
    except Exception as e:
        print(f"Error logging in user: {e}")
        return {"error": str(e)}
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def login_admin(email, password):
    """Login an admin"""
    connection = get_db_connection()
    if connection is None:
        return {"error": "Database connection failed"}
    
    cursor = connection.cursor()
    hashed_password = hash_password(password)
    
    try:
        # Check admin credentials
        query = "SELECT id, name FROM admins WHERE email = %s AND password = %s"
        cursor.execute(query, (email, hashed_password))
        admin = cursor.fetchone()
        
        if not admin:
            return {"error": "Invalid admin credentials"}
        
        # Generate token for the admin
        admin_id, name = admin
        token = generate_token(admin_id, name, True)
        
        print(f"Admin login successful: {name}, admin_id: {admin_id}, token: {token[:20]}...")
        
        return {
            "token": token,
            "admin_id": admin_id,
            "name": name
        }
    except Exception as e:
        print(f"Error logging in admin: {e}")
        return {"error": str(e)}
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def generate_token(user_id, name, is_admin):
    """Generate a JWT token for authentication"""
    payload = {
        "sub": str(user_id),  # Ensure user_id is converted to string
        "name": name,
        "is_admin": is_admin,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }
    
    print(f"Generating token with payload: {payload}")
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

def verify_token(token):
    """Verify a JWT token"""
    try:
        print(f"Verifying token: {token[:20]}...")
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        print(f"Token decoded successfully: {payload}")
        return payload
    except jwt.ExpiredSignatureError:
        print("Token verification failed: Token expired")
        return {"error": "Token expired"}
    except jwt.InvalidTokenError as e:
        print(f"Token verification failed: Invalid token - {str(e)}")
        return {"error": f"Invalid token: {str(e)}"}
    except Exception as e:
        print(f"Unexpected error during token verification: {str(e)}")
        return {"error": f"Token verification error: {str(e)}"}

def create_admin(name, email, password):
    """Create a new admin (called from terminal/script)"""
    connection = get_db_connection()
    if connection is None:
        return {"error": "Database connection failed"}
    
    cursor = connection.cursor()
    hashed_password = hash_password(password)
    
    try:
        # Check if email already exists
        cursor.execute("SELECT id FROM admins WHERE email = %s", (email,))
        if cursor.fetchone():
            return {"error": "Admin email already exists"}
        
        # Insert the new admin
        query = """
        INSERT INTO admins (name, email, password)
        VALUES (%s, %s, %s)
        """
        cursor.execute(query, (name, email, hashed_password))
        connection.commit()
        
        return {
            "success": True,
            "admin_id": cursor.lastrowid,
            "name": name
        }
    except Exception as e:
        print(f"Error creating admin: {e}")
        return {"error": str(e)}
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Function to extract token from headers
def get_user_id_from_token(auth_header):
    """Extract user ID from auth token"""
    if not auth_header:
        return None
        
    token = None
    if auth_header.startswith('Bearer '):
        token = auth_header[7:]
    else:
        parts = auth_header.split(" ")
        if len(parts) > 1:
            token = parts[1]
            
    if not token:
        return None
        
    payload = verify_token(token)
    if isinstance(payload, dict) and "error" not in payload:
        return payload.get("sub")  # user_id is stored in 'sub' claim
    return None

# Decorator for protected routes
def login_required(f):
    """Decorator to protect routes that require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"error": "Authentication required"}), 401
            
        token = None
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
        else:
            parts = auth_header.split(" ")
            if len(parts) > 1:
                token = parts[1]
                
        if not token:
            return jsonify({"error": "Invalid authentication token"}), 401
            
        payload = verify_token(token)
        if isinstance(payload, dict) and "error" in payload:
            return jsonify({"error": payload["error"]}), 401
            
        # Add user info to flask.g for the view function to use
        g.user_id = payload.get("sub")
        g.user_name = payload.get("name")
        g.is_admin = payload.get("is_admin", False)
        
        return f(*args, **kwargs)
    return decorated_function

# Decorator for admin-only routes
def admin_required(f):
    """Decorator to protect routes that require admin rights"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"error": "Authentication required"}), 401
            
        token = None
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
        else:
            parts = auth_header.split(" ")
            if len(parts) > 1:
                token = parts[1]
                
        if not token:
            return jsonify({"error": "Invalid authentication token"}), 401
            
        payload = verify_token(token)
        if isinstance(payload, dict) and "error" in payload:
            return jsonify({"error": payload["error"]}), 401
            
        # Check if user is admin
        if not payload.get("is_admin", False):
            return jsonify({"error": "Unauthorized access: Admin privileges required"}), 403
            
        # Add user info to flask.g for the view function to use
        g.user_id = payload.get("sub")
        g.user_name = payload.get("name")
        g.is_admin = True
        
        return f(*args, **kwargs)
    return decorated_function
