# app/businessLogic/excel_keeper.py

import time
import win32com.client
from sqlalchemy import create_engine, text
from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL
REFRESH_INTERVAL = 1800  # 30 minutes

engine = create_engine(DATABASE_URL)

def get_excel_paths():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT file_path FROM excel_file"))
        return [row[0] for row in result]


def run_excel_keeper():
    print("🚀 Excel Keeper Started")

    excel = win32com.client.Dispatch("Excel.Application")
    excel.Visible = False
    excel.DisplayAlerts = False

    workbooks = {}

    # Open all files
    for path in get_excel_paths():
        try:
            wb = excel.Workbooks.Open(path)
            workbooks[path] = wb
            print(f"✅ Opened: {path}")
        except Exception as e:
            print(f"❌ Failed: {path} -> {e}")

    # Loop forever
    while True:
        print("🔄 Refreshing all Excel files...")

        for path, wb in workbooks.items():
            try:
                wb.RefreshAll()
                wb.Save()
                print(f"✔ Refreshed: {path}")
            except Exception as e:
                print(f"⚠ Error refreshing {path}: {e}")

        time.sleep(REFRESH_INTERVAL)
