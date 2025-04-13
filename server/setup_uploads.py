
import os
import sys

def create_upload_directory():
    """Create the static/uploads directory for storing uploaded images"""
    # Define the path for uploads directory
    uploads_dir = os.path.join(os.path.dirname(__file__), "static", "uploads")
    
    # Create the directory if it doesn't exist
    try:
        os.makedirs(uploads_dir, exist_ok=True)
        print(f"Successfully created uploads directory at: {uploads_dir}")
        return True
    except Exception as e:
        print(f"Error creating uploads directory: {e}")
        return False

if __name__ == "__main__":
    # Run the function when script is executed directly
    success = create_upload_directory()
    sys.exit(0 if success else 1)
