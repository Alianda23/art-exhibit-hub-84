
#!/usr/bin/env python
"""
Flask server for the gallery web application.
"""

import os
import sys
import base64
import uuid
import traceback
from datetime import datetime
from flask import (
    Flask, request, jsonify, abort, 
    render_template, redirect, url_for, g, send_from_directory
)
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from functools import wraps

# Update imports to use correct database functions
from database import get_db_connection, dict_from_row, json_dumps
from auth import (
    verify_token, login_required, 
    admin_required, get_user_id_from_token
)
from artwork import (
    get_all_artworks, get_artwork, 
    create_artwork, update_artwork, delete_artwork
)
from exhibition import (
    get_all_exhibitions, get_exhibition, 
    create_exhibition, update_exhibition, delete_exhibition
)
from contact import create_contact_message, get_messages, update_message
from mpesa import initiate_stk_push

# Initialize Flask app
app = Flask(__name__)
app.config['DATABASE'] = os.path.join(os.path.dirname(__file__), 'gallery.db')

# Enable CORS
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# CORS middleware
def set_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

# Ensure upload directory exists
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Register middleware
app.after_request(set_cors_headers)

@app.route('/')
def index():
    return jsonify({"status": "success", "message": "Welcome to the Gallery API"})

# Serve static files from the static directory
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

# Process base64 image and save to file
def process_image_upload(image_data):
    if not image_data or not isinstance(image_data, str) or not image_data.startswith('data:'):
        print("Invalid image data:", image_data[:30] if image_data else "None")
        return None
        
    try:
        # Extract mimetype
        mimetype = image_data.split(';')[0].split(':')[1] if ';' in image_data and ':' in image_data else 'image/jpeg'
        print(f"Detected mimetype: {mimetype}")
        
        # Extract content after the comma
        if ',' in image_data:
            image_data = image_data.split(",")[1]
        else:
            print("No comma found in base64 string")
            return None
        
        # Get file extension from mimetype
        file_extension = "jpg"  # Default to jpg
        if "image/png" in mimetype:
            file_extension = "png"
        elif "image/jpeg" in mimetype or "image/jpg" in mimetype:
            file_extension = "jpg"
        elif "image/webp" in mimetype:
            file_extension = "webp"
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_image.{file_extension}"
        
        # Decode the base64 string
        try:
            image_binary = base64.b64decode(image_data)
            
            # Save to file
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            
            print(f"Saving image to: {filepath}")
            print(f"Directory exists: {os.path.exists(os.path.dirname(filepath))}")
            print(f"Directory is writable: {os.access(os.path.dirname(filepath), os.W_OK)}")
            
            with open(filepath, "wb") as f:
                f.write(image_binary)
                
            print(f"Image saved successfully, size: {len(image_binary)} bytes")
            
            # Verify file was actually created
            if os.path.exists(filepath):
                print(f"File exists after save: {os.path.getsize(filepath)} bytes")
            else:
                print("File does not exist after attempted save!")
                return None
                
            # Return the relative URL
            return f"/static/uploads/{filename}"
            
        except Exception as e:
            print(f"Error decoding base64 data: {e}")
            print(f"First 30 chars of data: {image_data[:30]}")
            return None
            
    except Exception as e:
        print(f"Error processing image: {e}")
        traceback.print_exc()
        return None

# Authentication routes
@app.route('/register', methods=['POST'])
def register():
    from auth import register_user
    data = request.get_json()
    result = register_user(data.get('name'), data.get('email'), data.get('password'), data.get('phone'))
    return jsonify(result)

@app.route('/login', methods=['POST'])
def login():
    from auth import login_user
    data = request.get_json()
    result = login_user(data.get('email'), data.get('password'))
    return jsonify(result)

@app.route('/admin-login', methods=['POST'])
def admin_login():
    from auth import login_admin
    data = request.get_json()
    result = login_admin(data.get('email'), data.get('password'))
    return jsonify(result)

# Artwork routes
@app.route('/api/artworks', methods=['GET'])
def artworks():
    try:
        all_artworks = get_all_artworks()
        return jsonify(all_artworks)
    except Exception as e:
        print(f"Error fetching artworks: {e}")
        return jsonify({"status": "error", "message": "Failed to fetch artworks"}), 500

@app.route('/api/artworks/<int:artwork_id>', methods=['GET'])
def artwork(artwork_id):
    try:
        artwork = get_artwork(artwork_id)
        if not artwork:
            return jsonify({"status": "error", "message": "Artwork not found"}), 404
        return jsonify(artwork)
    except Exception as e:
        print(f"Error fetching artwork: {e}")
        return jsonify({"status": "error", "message": "Failed to fetch artwork"}), 500

@app.route('/api/artworks', methods=['POST'])
@admin_required
def add_artwork():
    try:
        data = request.get_json()
        
        # Process image if it's a base64 string
        if data.get('imageUrl') and data['imageUrl'].startswith('data:'):
            print("Processing base64 image from artwork submission")
            image_url = process_image_upload(data['imageUrl'])
            if image_url:
                print(f"Image successfully processed and saved: {image_url}")
                data['imageUrl'] = image_url
            else:
                print("Failed to process image, using default")
                return jsonify({
                    "status": "error", 
                    "message": "Failed to process image"
                }), 400
        
        print(f"Inserting artwork data: {data}")
        result = create_artwork(request.headers.get('Authorization'), data)
        
        if "error" in result:
            return jsonify({"status": "error", "message": result["error"]}), 400
            
        return jsonify({
            "status": "success", 
            "message": "Artwork created successfully",
            "artwork": result
        }), 201
    except Exception as e:
        print(f"Error creating artwork: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": f"Failed to create artwork: {str(e)}"}), 500

@app.route('/api/artworks/<int:artwork_id>', methods=['PUT'])
@admin_required
def update_artwork_route(artwork_id):
    try:
        data = request.get_json()
        
        # Process image if it's a base64 string
        if data.get('imageUrl') and data['imageUrl'].startswith('data:'):
            print("Processing base64 image from artwork update")
            image_url = process_image_upload(data['imageUrl'])
            if image_url:
                print(f"Image successfully processed and saved: {image_url}")
                data['imageUrl'] = image_url
            else:
                print("Failed to process image, responding with error")
                return jsonify({
                    "status": "error", 
                    "message": "Failed to process image"
                }), 400
        
        result = update_artwork(request.headers.get('Authorization'), artwork_id, data)
        
        if "error" in result:
            return jsonify({"status": "error", "message": result["error"]}), 400 if result["error"] != "Artwork not found" else 404
            
        return jsonify({
            "status": "success", 
            "message": "Artwork updated successfully",
            "artwork": result
        })
    except Exception as e:
        print(f"Error updating artwork: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": f"Failed to update artwork: {str(e)}"}), 500

@app.route('/api/artworks/<int:artwork_id>', methods=['DELETE'])
@admin_required
def delete_artwork_route(artwork_id):
    try:
        result = delete_artwork(request.headers.get('Authorization'), artwork_id)
        
        if "error" in result:
            return jsonify({"status": "error", "message": result["error"]}), 400 if result["error"] != "Artwork not found" else 404
            
        return jsonify({
            "status": "success", 
            "message": "Artwork deleted successfully"
        })
    except Exception as e:
        print(f"Error deleting artwork: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": f"Failed to delete artwork: {str(e)}"}), 500

# Exhibition routes
@app.route('/api/exhibitions', methods=['GET'])
def exhibitions():
    try:
        all_exhibitions = get_all_exhibitions()
        return jsonify(all_exhibitions)
    except Exception as e:
        print(f"Error fetching exhibitions: {e}")
        return jsonify({"status": "error", "message": "Failed to fetch exhibitions"}), 500

@app.route('/api/exhibitions/<int:exhibition_id>', methods=['GET'])
def exhibition(exhibition_id):
    try:
        exhibition = get_exhibition(exhibition_id)
        if not exhibition:
            return jsonify({"status": "error", "message": "Exhibition not found"}), 404
        return jsonify(exhibition)
    except Exception as e:
        print(f"Error fetching exhibition: {e}")
        return jsonify({"status": "error", "message": "Failed to fetch exhibition"}), 500

@app.route('/api/exhibitions', methods=['POST'])
@admin_required
def add_exhibition():
    try:
        data = request.get_json()
        
        # Process image if it's a base64 string
        if data.get('imageUrl') and data['imageUrl'].startswith('data:'):
            print("Processing base64 image from exhibition submission")
            image_url = process_image_upload(data['imageUrl'])
            if image_url:
                print(f"Image successfully processed and saved: {image_url}")
                data['imageUrl'] = image_url
            else:
                print("Failed to process image, responding with error")
                return jsonify({
                    "status": "error", 
                    "message": "Failed to process image"
                }), 400
        
        result = create_exhibition(request.headers.get('Authorization'), data)
        
        if "error" in result:
            return jsonify({"status": "error", "message": result["error"]}), 400
            
        return jsonify({
            "status": "success", 
            "message": "Exhibition created successfully",
            "exhibition": result
        }), 201
    except Exception as e:
        print(f"Error creating exhibition: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": f"Failed to create exhibition: {str(e)}"}), 500

@app.route('/api/exhibitions/<int:exhibition_id>', methods=['PUT'])
@admin_required
def update_exhibition_route(exhibition_id):
    try:
        data = request.get_json()
        
        # Process image if it's a base64 string
        if data.get('imageUrl') and data['imageUrl'].startswith('data:'):
            print("Processing base64 image from exhibition update")
            image_url = process_image_upload(data['imageUrl'])
            if image_url:
                print(f"Image successfully processed and saved: {image_url}")
                data['imageUrl'] = image_url
            else:
                print("Failed to process image, responding with error")
                return jsonify({
                    "status": "error", 
                    "message": "Failed to process image"
                }), 400
        
        result = update_exhibition(request.headers.get('Authorization'), exhibition_id, data)
        
        if "error" in result:
            return jsonify({"status": "error", "message": result["error"]}), 400 if result["error"] != "Exhibition not found" else 404
            
        return jsonify({
            "status": "success", 
            "message": "Exhibition updated successfully",
            "exhibition": result
        })
    except Exception as e:
        print(f"Error updating exhibition: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": f"Failed to update exhibition: {str(e)}"}), 500

@app.route('/api/exhibitions/<int:exhibition_id>', methods=['DELETE'])
@admin_required
def delete_exhibition_route(exhibition_id):
    try:
        result = delete_exhibition(request.headers.get('Authorization'), exhibition_id)
        
        if "error" in result:
            return jsonify({"status": "error", "message": result["error"]}), 400 if result["error"] != "Exhibition not found" else 404
            
        return jsonify({
            "status": "success", 
            "message": "Exhibition deleted successfully"
        })
    except Exception as e:
        print(f"Error deleting exhibition: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": f"Failed to delete exhibition: {str(e)}"}), 500

# Contact routes
@app.route('/contact', methods=['POST'])
def contact():
    data = request.get_json()
    result = create_contact_message(data)
    return jsonify(result)

@app.route('/messages', methods=['GET'])
@admin_required
def messages():
    auth_header = request.headers.get('Authorization')
    result = get_messages(auth_header)
    return jsonify(result)

@app.route('/messages/<int:message_id>', methods=['PUT'])
@admin_required
def update_message_route(message_id):
    auth_header = request.headers.get('Authorization')
    data = request.get_json()
    result = update_message(auth_header, message_id, data)
    return jsonify(result)

# Payment routes
@app.route('/mpesa/stk-push', methods=['POST'])
def stk_push():
    data = request.get_json()
    phone_number = data.get('phoneNumber')
    amount = data.get('amount')
    order_type = data.get('orderType')
    order_id = data.get('orderId')
    user_id = data.get('userId')
    account_reference = data.get('accountReference')
    
    try:
        response = initiate_stk_push(phone_number, amount, account_reference, order_type, order_id, user_id)
        return jsonify(response)
    except Exception as e:
        print(f"M-Pesa Error: {e}")
        return jsonify({"error": str(e)}), 500

# Create functions to set up the database and upload directory
def create_upload_directory():
    """Create the static/uploads directory for storing uploaded images"""
    # Define the path for uploads directory
    uploads_dir = os.path.join(os.path.dirname(__file__), "static", "uploads")
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    
    # Create the directories if they don't exist
    try:
        os.makedirs(uploads_dir, exist_ok=True)
        print(f"Successfully created uploads directory at: {uploads_dir}")
        
        # Add a .gitkeep file to ensure the directory is tracked by git
        with open(os.path.join(uploads_dir, ".gitkeep"), "w") as f:
            f.write("# This file ensures the uploads directory is tracked by git\n")
        
        # Add proper permissions to the directory - make it world-writable
        try:
            os.chmod(uploads_dir, 0o777)  # rwxrwxrwx permissions
            print("Set permissive 0o777 permissions on uploads directory for maximum compatibility")
            
            # Also set parent directory permissions
            os.chmod(static_dir, 0o777)
            print("Set permissive permissions on static directory")
        except Exception as e:
            print(f"Warning: Could not set permissions on directory: {e}")
            
        # Verify directory is writable
        test_file = os.path.join(uploads_dir, "test_write.txt")
        try:
            with open(test_file, "w") as f:
                f.write("Testing write permissions\n")
            if os.path.exists(test_file):
                os.remove(test_file)
                print("Verified directory is writable")
            else:
                print("WARNING: Directory write test failed!")
        except Exception as e:
            print(f"WARNING: Directory is not writable: {e}")
            
        return True
    except Exception as e:
        print(f"Error creating uploads directory: {e}")
        return False

def verify_static_serving():
    """Verify that static files are properly served"""
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    
    # Ensure static directory exists
    os.makedirs(static_dir, exist_ok=True)
    
    test_file_path = os.path.join(static_dir, "test.txt")
    
    try:
        # Create a test file in the static directory
        with open(test_file_path, "w") as f:
            f.write("Test file for static serving\n")
        
        print("Created test file for static serving")
        
        # Add a placeholder image
        placeholder_path = os.path.join(static_dir, "placeholder.svg")
        if not os.path.exists(placeholder_path):
            try:
                # Create a simple SVG placeholder
                with open(placeholder_path, "w") as f:
                    f.write('''<svg width="300" height="300" xmlns="http://www.w3.org/2000/svg">
                        <rect width="300" height="300" fill="#f0f0f0"/>
                        <text x="50%" y="50%" font-family="Arial" font-size="24" fill="#999" text-anchor="middle">Image Placeholder</text>
                    </svg>''')
                print("Created placeholder SVG in static directory")
            except Exception as e:
                print(f"Warning: Could not create placeholder SVG: {e}")
        
        return True
    except Exception as e:
        print(f"Error verifying static serving: {e}")
        return False
    finally:
        # Clean up test file
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

# Main entry point
if __name__ == '__main__':
    # Initialize the upload directory and static file serving
    try:
        create_upload_directory()
        verify_static_serving()
        print("Upload directory and static serving initialized successfully.")
    except Exception as e:
        print(f"Error initializing upload directory: {e}")
        traceback.print_exc()
    
    # Initialize the database table structure
    try:
        # Use MySQL-specific initialization
        from db_setup import initialize_database
        initialize_database()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)
    
    # Check upload directory permissions
    try:
        test_file_path = os.path.join(UPLOAD_FOLDER, "test_permissions.txt")
        with open(test_file_path, "w") as f:
            f.write("Testing write permissions\n")
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
            print(f"Upload directory {UPLOAD_FOLDER} is writable")
        else:
            print(f"Failed to verify write permissions for {UPLOAD_FOLDER}")
    except Exception as e:
        print(f"Error checking upload directory permissions: {e}")
        print("Attempting to set permissions...")
        try:
            # Try to set more permissive permissions
            os.chmod(UPLOAD_FOLDER, 0o777)  # rwxrwxrwx
            print("Set permissions to 0o777 for uploads directory")
        except Exception as e:
            print(f"Failed to set permissions: {e}")
    
    # Start the Flask server
    app.run(debug=True, host='0.0.0.0', port=8000)
