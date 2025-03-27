import subprocess
import schedule
import time
from datetime import datetime

# Function to run the BibTeX generator script
def run_bibtex_generator():
    print(f"[{datetime.now()}] Running BibTeX generator script...")
    try:
        # Run the generate_bibtex.py script
        result = subprocess.run(["python3.9", "src/scripts/generate_bibtex.py"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[{datetime.now()}] BibTeX generation completed successfully!")
        else:
            print(f"[{datetime.now()}] Error running BibTeX generator:\n{result.stderr}")
    except Exception as e:
        print(f"[{datetime.now()}] Exception occurred: {e}")

# Schedule the task to run every two weeks
schedule.every(2).weeks.do(run_bibtex_generator)

# Run immediately once on script start
run_bibtex_generator()

print(f"[{datetime.now()}] Scheduler started. Waiting for the next execution...")

# Keep the script running to execute scheduled tasks
while True:
    schedule.run_pending()
    time.sleep(1)  # Sleep for a second to prevent high CPU usage
