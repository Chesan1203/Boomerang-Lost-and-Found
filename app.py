import subprocess
import sys
import time

# Start FastAPI (main.py)
subprocess.Popen([sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"])
time.sleep(5)
# Start Streamlit (interface.py) on HF's public port
subprocess.run([sys.executable, "-m", "streamlit", "run", "interface.py", "--server.port", "7860", "--server.address", "0.0.0.0"])