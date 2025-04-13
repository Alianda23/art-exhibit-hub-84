
#!/usr/bin/env python
"""
Startup script that initializes the server environment and starts the server.
"""

import os
import sys
import subprocess
from setup_uploads import create_upload_directory, verify_static_serving

def main():
    """Main function to set up environment and start server"""
    print("Setting up environment...")
    
    # Create uploads directory
    print("Creating uploads directory...")
    success = create_upload_directory()
    if not success:
        print("Failed to create uploads directory, exiting.")
        sys.exit(1)
    
    # Verify static files serving
    print("Verifying static files serving...")
    verify_static_serving()
    
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
