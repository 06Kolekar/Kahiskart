from apscheduler.schedulers.background import BackgroundScheduler
import requests

scheduler = BackgroundScheduler()

def notify_powerbi():
    print("Triggering Power BI refresh...")
    requests.post("YOUR_POWER_BI_WEBHOOK_URL")

def start_scheduler():
    scheduler.add_job(notify_powerbi, "interval", minutes=29)
    scheduler.start()
