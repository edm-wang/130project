import json
import time
import os
from urllib.request import Request, urlopen

from dotenv import load_dotenv

load_dotenv("app/supabase/.env")

url = "http://localhost:8000/internal/jobs/paper-ingestion"
secret = os.getenv("SUPABASE_CRON_JOB_SECRET")

payload = {
    "categories": ["cs.AI"],
    "max_results": 10,
}
interval = 60 * 60 * 24

while True:
    request = Request(
        url=url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "x-cron-job-secret": secret,
            "Content-Type": "application/json"
        },
        method="POST"
    )

    with urlopen(request, timeout=120) as response:
        print(response.status)
        print(response.read().decode("utf-8"))
    
    time.sleep(interval)