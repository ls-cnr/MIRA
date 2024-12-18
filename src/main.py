import subprocess
import sys
import os

# List of required packages
required_packages = ["flask", "langchain", "ollama"]

# Function to install a package
def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Check and install missing packages
for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        print(f"{package} is not installed. Installing...")
        install_package(package)

# Run the `conversation.py` script
if __name__ == "__main__":
    script_path = "conversation.py"
    if os.path.exists(script_path):
        subprocess.run([sys.executable, script_path])
    else:
        print(f"Error: {script_path} not found.")