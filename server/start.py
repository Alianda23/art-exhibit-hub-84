
#!/usr/bin/env python
"""
Startup script that initializes the server environment and starts the server.
"""

import os
import sys
import subprocess
from setup_uploads import create_upload_directory, verify_static_serving, print_directory_structure

def main():
    """Main function to set up environment and start server"""
    print("Setting up environment...")
    
    # Create uploads directory with proper permissions
    print("Creating uploads directory...")
    success = create_upload_directory()
    if not success:
        print("Failed to create uploads directory, exiting.")
        sys.exit(1)
    
    # Verify static files serving
    print("Verifying static files serving...")
    verify_static_serving()
    
    # Print directory structure for debugging
    print_directory_structure()
    
    # Define uploads directory path
    uploads_dir = os.path.join(os.path.dirname(__file__), "static", "uploads")
    
    # Check if uploads directory is writable
    if not os.path.exists(uploads_dir):
        print(f"ERROR: Uploads directory does not exist: {uploads_dir}")
        sys.exit(1)
    
    if not os.access(uploads_dir, os.W_OK):
        print(f"WARNING: Uploads directory is not writable: {uploads_dir}")
        print("Attempting to set permissions...")
        try:
            os.chmod(uploads_dir, 0o777)  # rwxrwxrwx
            print("Set permissions to 0o777")
        except Exception as e:
            print(f"Failed to set permissions: {e}")
            
        # Verify if permissions were set correctly
        if not os.access(uploads_dir, os.W_OK):
            print("Directory is still not writable after permission change!")
        else:
            print("Directory is now writable.")
    
    # Test file creation in uploads directory
    test_file = os.path.join(uploads_dir, "test_startup.txt")
    try:
        with open(test_file, "w") as f:
            f.write(f"Test file created by start.py at {os.path.abspath(test_file)}\n")
        if os.path.exists(test_file):
            print(f"Successfully created test file: {test_file}")
            os.remove(test_file)
            print("Test file removed.")
        else:
            print("Failed to create test file!")
    except Exception as e:
        print(f"Error creating test file: {e}")
    
    # Start the server
    print("Starting server...")
    try:
        # Use the same Python interpreter that started this script
        python_executable = sys.executable
        subprocess.run([python_executable, "server.py"], cwd=os.path.dirname(__file__))
    except KeyboardInterrupt:
        print("Server stopped by user.")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
