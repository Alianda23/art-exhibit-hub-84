
import os
import sys
import shutil

def create_upload_directory():
    """Create the static/uploads directory for storing uploaded images"""
    # Define the path for uploads directory
    uploads_dir = os.path.join(os.path.dirname(__file__), "static", "uploads")
    
    # Create the directory if it doesn't exist
    try:
        os.makedirs(uploads_dir, exist_ok=True)
        print(f"Successfully created uploads directory at: {uploads_dir}")
        
        # Add a .gitkeep file to ensure the directory is tracked by git
        with open(os.path.join(uploads_dir, ".gitkeep"), "w") as f:
            f.write("# This file ensures the uploads directory is tracked by git\n")
        
        # Add proper permissions to the directory
        try:
            os.chmod(uploads_dir, 0o755)  # rwxr-xr-x permissions
            print("Set proper permissions on uploads directory")
        except Exception as e:
            print(f"Warning: Could not set permissions on directory: {e}")
            
        return True
    except Exception as e:
        print(f"Error creating uploads directory: {e}")
        return False

def verify_static_serving():
    """Verify that static files are properly served"""
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    test_file_path = os.path.join(static_dir, "test.txt")
    
    try:
        # Create a test file in the static directory
        with open(test_file_path, "w") as f:
            f.write("Test file for static serving\n")
        
        print("Created test file for static serving")
        
        # Add a placeholder image
        placeholder_path = os.path.join(static_dir, "placeholder.jpg")
        if not os.path.exists(placeholder_path):
            try:
                # Create a simple 1x1 pixel image
                with open(placeholder_path, "wb") as f:
                    # Simple 1x1 black JPEG
                    f.write(b'\xff\xd8\xff\xe0\x00\x10\x4a\x46\x49\x46\x00\x01\x01\x01\x00\x48\x00\x48\x00\x00\xff\xdb\x00\x43\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\x09\x09\x08\x0a\x0c\x14\x0d\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c\x20\x24\x2e\x27\x20\x22\x2c\x23\x1c\x1c\x28\x37\x29\x2c\x30\x31\x34\x34\x34\x1f\x27\x39\x3d\x38\x32\x3c\x2e\x33\x34\x32\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x08\x01\x01\x00\x00\x3f\x00\x7f\xff\xd9')
                print("Created placeholder image in static directory")
            except Exception as e:
                print(f"Warning: Could not create placeholder image: {e}")
        
        return True
    except Exception as e:
        print(f"Error verifying static serving: {e}")
        return False
    finally:
        # Clean up test file
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

if __name__ == "__main__":
    # Run the function when script is executed directly
    success = create_upload_directory()
    if success:
        verify_static_serving()
    sys.exit(0 if success else 1)
