import win32serviceutil
import win32service
import win32event
import subprocess

class BackendService(win32serviceutil.ServiceFramework):
    _svc_name_ = "KahiskartBackend"
    _svc_display_name_ = "Kahiskart Backend Service"
    _svc_description_ = "Runs FastAPI backend automatically"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.process = None

    def SvcDoRun(self):
        self.process = subprocess.Popen([
            "uvicorn", "app.main:app",
            "--host", "0.0.0.0",
            "--port", "8000"
        ])
        win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)

    def SvcStop(self):
        if self.process:
            self.process.terminate()
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)
        win32event.SetEvent(self.stop_event)

if __name__ == "__main__":
    win32serviceutil.HandleCommandLine(BackendService)
