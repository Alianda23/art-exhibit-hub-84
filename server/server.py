
#!/usr/bin/env python
"""
Flask server for the gallery web application.
"""

import os
import sys
import base64
import uuid
from datetime import datetime
from flask import (
    Flask, request, jsonify, abort, 
    render_template, redirect, url_for, g, send_from_directory
)
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

from database import get_db, close_db, init_db
from auth import (
    generate_token, decode_token, login_required, 
    admin_required, get_user_id_from_token
)
from artwork import (
    get_all_artworks, get_artwork_by_id, 
    create_artwork, update_artwork, delete_artwork
)
from exhibition import (
    get_all_exhibitions, get_exhibition_by_id, 
    create_exhibition, update_exhibition, delete_exhibition
)
from contact import create_contact_message, get_all_messages
from mpesa import initiate_stk_push
from middleware import set_cors_headers

# Initialize Flask app
app = Flask(__name__)
app.config['DATABASE'] = os.path.join(os.path.dirname(__file__), 'gallery.db')

# Enable CORS
CORS(app)

# Register database connection and close functions
app.teardown_appcontext(close_db)

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
    if not image_data or not image_data.startswith('data:'):
        return None
        
    try:
        # Extract content after the comma
        image_data = image_data.split(",")[1]
        
        # Get file extension from mimetype
        file_extension = "jpg"  # Default to jpg
        if "image/png" in image_data:
            file_extension = "png"
        elif "image/jpeg" in image_data or "image/jpg" in image_data:
            file_extension = "jpg"
        elif "image/webp" in image_data:
            file_extension = "webp"
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_image.{file_extension}"
        
        # Decode the base64 string
        image_binary = base64.b64decode(image_data)
        
        # Save to file
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        with open(filepath, "wb") as f:
            f.write(image_binary)
            
        # Return the relative URL
        return f"/static/uploads/{filename}"
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

# Authentication routes
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password') or not data.get('name'):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400
    
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Check if user exists
        cursor.execute("SELECT * FROM users WHERE email = ?", (data['email'],))
        user = cursor.fetchone()
        
        if user:
            return jsonify({"status": "error", "message": "User already exists"}), 400
        
        # Create new user
        hashed_password = generate_password_hash(data['password'])
        cursor.execute(
            "INSERT INTO users (name, email, password, is_admin) VALUES (?, ?, ?, ?)",
            (data['name'], data['email'], hashed_password, False)
        )
        db.commit()
        
        return jsonify({"status": "success", "message": "User registered successfully"}), 201
    
    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({"status": "error", "message": "Registration failed"}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"status": "error", "message": "Missing email or password"}), 400
    
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Find user
        cursor.execute(
            "SELECT id, name, email, password, is_admin FROM users WHERE email = ?",
            (data['email'],)
        )
        user = cursor.fetchone()
        
        if not user or not check_password_hash(user['password'], data['password']):
            return jsonify({"status": "error", "message": "Invalid credentials"}), 401
        
        # Generate token
        token = generate_token(user['id'], user['is_admin'])
        
        return jsonify({
            "status": "success",
            "message": "Login successful",
            "token": token,
            "user": {
                "id": user['id'],
                "name": user['name'],
                "email": user['email'],
                "is_admin": bool(user['is_admin'])
            }
        })
    
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({"status": "error", "message": "Login failed"}), 500

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
        artwork = get_artwork_by_id(artwork_id)
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
            image_url = process_image_upload(data['imageUrl'])
            if image_url:
                data['imageUrl'] = image_url
            else:
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
        return jsonify({"status": "error", "message": f"Failed to create artwork: {str(e)}"}), 500

@app.route('/api/artworks/<int:artwork_id>', methods=['PUT'])
@admin_required
def update_artwork_route(artwork_id):
    try:
        data = request.get_json()
        
        # Process image if it's a base64 string
        if data.get('imageUrl') and data['imageUrl'].startswith('data:'):
            image_url = process_image_upload(data['imageUrl'])
            if image_url:
                data['imageUrl'] = image_url
            else:
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
        return jsonify({"status": "error", "message": "Failed to delete artwork"}), 500

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
        exhibition = get_exhibition_by_id(exhibition_id)
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
            image_url = process_image_upload(data['imageUrl'])
            if image_url:
                data['imageUrl'] = image_url
            else:
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
        return jsonify({"status": "error", "message": f"Failed to create exhibition: {str(e)}"}), 500

@app.route('/api/exhibitions/<int:exhibition_id>', methods=['PUT'])
@admin_required
def update_exhibition_route(exhibition_id):
    try:
        data = request.get_json()
        
        # Process image if it's a base64 string
        if data.get('imageUrl') and data['imageUrl'].startswith('data:'):
            image_url = process_image_upload(data['imageUrl'])
            if image_url:
                data['imageUrl'] = image_url
            else:
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
        return jsonify({"status": "error", "message": "Failed to delete exhibition"}), 500

# Contact routes
@app.route('/api/contact', methods=['POST'])
def contact():
    try:
        data = request.get_json()
        message_id = create_contact_message(data)
        return jsonify({
            "status": "success", 
            "message": "Message sent successfully",
            "id": message_id
        }), 201
    except Exception as e:
        print(f"Error creating contact message: {e}")
        return jsonify({"status": "error", "message": "Failed to send message"}), 500

@app.route('/api/messages', methods=['GET'])
@admin_required
def messages():
    try:
        all_messages = get_all_messages()
        return jsonify(all_messages)
    except Exception as e:
        print(f"Error fetching messages: {e}")
        return jsonify({"status": "error", "message": "Failed to fetch messages"}), 500

# Payment routes
@app.route('/api/payments/mpesa', methods=['POST'])
@login_required
def mpesa_payment():
    try:
        data = request.get_json()
        result = initiate_stk_push(data)
        return jsonify(result)
    except Exception as e:
        print(f"Error processing payment: {e}")
        return jsonify({"status": "error", "message": "Payment processing failed"}), 500

# Main entry point
if __name__ == '__main__':
    # Initialize the database if it doesn't exist
    try:
        init_db()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)
    
    # Start the Flask server
    app.run(debug=True, host='0.0.0.0')
