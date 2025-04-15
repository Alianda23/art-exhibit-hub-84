
import os
import sys
import shutil

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
        
        # Also add a placeholder jpg for systems that require jpg format
        placeholder_jpg_path = os.path.join(static_dir, "placeholder.jpg")
        if not os.path.exists(placeholder_jpg_path):
            try:
                # Create a simple file with minimum valid JPG content
                with open(placeholder_jpg_path, "wb") as f:
                    # Simple 1x1 black JPEG
                    f.write(b'\xff\xd8\xff\xe0\x00\x10\x4a\x46\x49\x46\x00\x01\x01\x01\x00\x48\x00\x48\x00\x00\xff\xdb\x00\x43\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\x09\x09\x08\x0a\x0c\x14\x0d\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c\x20\x24\x2e\x27\x20\x22\x2c\x23\x1c\x1c\x28\x37\x29\x2c\x30\x31\x34\x34\x34\x1f\x27\x39\x3d\x38\x32\x3c\x2e\x33\x34\x32\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x08\x01\x01\x00\x00\x3f\x00\x7f\xff\xd9')
                print("Created placeholder JPG in static directory")
            except Exception as e:
                print(f"Warning: Could not create placeholder JPG: {e}")
        
        return True
    except Exception as e:
        print(f"Error verifying static serving: {e}")
        return False
    finally:
        # Clean up test file
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

def print_directory_structure():
    """Print the directory structure for debugging"""
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    
    if os.path.exists(static_dir):
        print("\nStatic directory structure:")
        print(f"- {static_dir}")
        
        # List all items in the static directory
        for item in os.listdir(static_dir):
            item_path = os.path.join(static_dir, item)
            if os.path.isdir(item_path):
                print(f"  - {item}/ (directory)")
                
                # List items in subdirectories
                if os.path.exists(item_path):
                    try:
                        subitems = os.listdir(item_path)
                        for subitem in subitems:
                            print(f"    - {subitem}")
                    except Exception as e:
                        print(f"    Error reading directory: {e}")
            else:
                print(f"  - {item} (file, {os.path.getsize(item_path)} bytes)")
    else:
        print(f"\nStatic directory does not exist: {static_dir}")

if __name__ == "__main__":
    # Run the function when script is executed directly
    success = create_upload_directory()
    if success:
        verify_static_serving()
        print_directory_structure()
    sys.exit(0 if success else 1)
