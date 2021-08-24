#========================================
# Scheduler Jobs
#========================================
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc
scheduler = BackgroundScheduler()
scheduler.configure(timezone=utc)

# jobs
import scheduler_jobs

scheduler.add_job(scheduler_jobs.check_system_status, 'interval', minutes=15)

scheduler.start()

#========================================