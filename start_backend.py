import subprocess
import time

# Start FastAPI server
subprocess.Popen([
    "uvicorn", "app.main:app",
    "--host", "0.0.0.0",
    "--port", "8000"
])

# Keep script alive
while True:
    time.sleep(60)
