from app import create_app
import atexit

import time
import sys
from apscheduler.schedulers.background import BackgroundScheduler

from app.modules.controller import quiz_dates

def job_function():
    quiz_dates()

app = create_app()
sched = BackgroundScheduler(daemon=True)
sched.add_job(job_function,'interval',minutes=4)
sched.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0',port='5000')