import os
import sys
from apscheduler.schedulers.blocking import BlockingScheduler

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.job_agent import run_agent


def scheduled_job():
    print(f"\n{'='*60}")
    print("Running scheduled job search...")
    print(f"{'='*60}\n")
    run_agent(query="machine learning engineer", location="Bangalore", top_k=5)


if __name__ == "__main__":
    scheduler = BlockingScheduler()

    # Run once immediately on startup
    scheduled_job()

    # Then run every day at 9:00 AM
    scheduler.add_job(scheduled_job, "cron", hour=9, minute=0)

    print("\nScheduler started. Job will run daily at 9:00 AM.")
    print("Press Ctrl+C to stop.\n")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\nScheduler stopped.")