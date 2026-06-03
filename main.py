# main.py - LeadRadar Pro Entry Point
# This file runs the main Streamlit application

import subprocess
import sys

if __name__ == "__main__":
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
