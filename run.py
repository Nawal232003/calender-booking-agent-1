import subprocess, threading, webbrowser, time

def run_backend():
    subprocess.Popen(["uvicorn", "backend.main:app", "--reload"])

def run_frontend():
    time.sleep(3)
    subprocess.Popen(["streamlit", "run", "frontend/streamlit_app.py"])

def open_browser():
    time.sleep(5)
    webbrowser.open("http://localhost:8501")

if __name__ == "__main__":
    run_backend()
    run_frontend()
    open_browser()
    while True:
        time.sleep(1)
