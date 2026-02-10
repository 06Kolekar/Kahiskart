import win32serviceutil
import win32service
import win32event
import servicemanager
import subprocess
import time
import sys
import os

class KahiskartBackendService(win32serviceutil.ServiceFramework):
    _svc_name_ = "KahiskartBackendService"
    _svc_display_name_ = "Kahiskart Backend Service"
    _svc_description_ = "Runs FastAPI backend and Excel ingestion system in background"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.process = None

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        if self.process:
            self.process.terminate()
        win32event.SetEvent(self.stop_event)

    def SvcDoRun(self):
        servicemanager.LogInfoMsg("KahiskartBackendService starting...")

        #  IMPORTANT: correct python + backend path
        python_exe = sys.executable
        backend_main = r"C:\Users\abhis\OneDrive\Documents\WebArcligthIntern\PYTHON\Kahiskart\back-end\app\main.py"

        # Start FastAPI as subprocess
        self.process = subprocess.Popen(
            [python_exe, backend_main],
            cwd=os.path.dirname(backend_main),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        #  Tell Windows service manager we are running
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)

        # Keep service alive
        win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(KahiskartBackendService)
