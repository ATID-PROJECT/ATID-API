from app import create_app

import schedule
import time
import sys

from app.modules.controller import quiz_dates

def job():
    #quiz_dates()
    a = 5

schedule.every(1).minutes.do(job)

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0',port='5000')

    while True:
        schedule.run_pending()
        time.sleep(1)
