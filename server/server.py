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

# Update imports to use correct database functions
from database import get_db_connection, save_contact_message, get_all_contact_messages
from auth import (
    generate_token, verify_token, login_required, 
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
from contact import create_contact_message, get_messages
from mpesa import initiate_stk_push
from middleware import set_cors_headers

# Initialize Flask app
app = Flask(__name__)
app.config['DATABASE'] = os.path.join(os.path.dirname(__file__), 'gallery.db')

# Enable CORS
CORS(app)

# Remove the database connection teardown since we're using different db functions
# app.teardown_appcontext(close_db)

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
    data = request.get_json()
    result = auth.register_user(data.get('name'), data.get('email'), data.get('password'), data.get('phone'))
    return jsonify(result)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    result = auth.login_user(data.get('email'), data.get('password'))
    return jsonify(result)

@app.route('/admin-login', methods=['POST'])
def admin_login():
    data = request.get_json()
    result = auth.login_admin(data.get('email'), data.get('password'))
    return jsonify(result)

# Middleware to verify token
def verify_token_middleware(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 403
        try:
            data = auth.decode_token(token)
        except:
            return jsonify({'message': 'Token is invalid'}), 403
        return f(*args, **kwargs)
    return decorated

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
        artwork_id = create_artwork(data)
        return jsonify({
            "status": "success", 
            "message": f"Artwork created successfully with ID: {artwork_id}",
            "id": artwork_id
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
        
        success = update_artwork(artwork_id, data)
        if not success:
            return jsonify({"status": "error", "message": "Artwork not found"}), 404
        return jsonify({"status": "success", "message": "Artwork updated successfully"})
    except Exception as e:
        print(f"Error updating artwork: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": f"Failed to update artwork: {str(e)}"}), 500

@app.route('/api/artworks/<int:artwork_id>', methods=['DELETE'])
@admin_required
def delete_artwork_route(artwork_id):
    try:
        success = delete_artwork(artwork_id)
        if not success:
            return jsonify({"status": "error", "message": "Artwork not found"}), 404
        return jsonify({"status": "success", "message": "Artwork deleted successfully"})
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
        
        exhibition_id = create_exhibition(data)
        return jsonify({
            "status": "success", 
            "message": "Exhibition created successfully",
            "id": exhibition_id
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
        
        success = update_exhibition(exhibition_id, data)
        if not success:
            return jsonify({"status": "error", "message": "Exhibition not found"}), 404
        return jsonify({"status": "success", "message": "Exhibition updated successfully"})
    except Exception as e:
        print(f"Error updating exhibition: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": f"Failed to update exhibition: {str(e)}"}), 500

@app.route('/api/exhibitions/<int:exhibition_id>', methods=['DELETE'])
@admin_required
def delete_exhibition_route(exhibition_id):
    try:
        success = delete_exhibition(exhibition_id)
        if not success:
            return jsonify({"status": "error", "message": "Exhibition not found"}), 404
        return jsonify({"status": "success", "message": "Exhibition deleted successfully"})
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
        response = initiate_stk_push(phone_number, amount, order_type, order_id, user_id, account_reference)
        return jsonify(response)
    except Exception as e:
        print(f"M-Pesa Error: {e}")
        return jsonify({"error": str(e)}), 500

# Main entry point
if __name__ == '__main__':
    # Initialize the database table structure (moved init_db logic)
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
    app.run(debug=True, host='0.0.0.0')
