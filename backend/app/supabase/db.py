
import os
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client

load_dotenv(Path(__file__).with_name(".env"))
load_dotenv()

db_url = os.environ.get("SUPABASE_URL")
db_key = (
    os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    or os.environ.get("SUPABASE_SECRET_KEY")
    or os.environ.get("SUPABASE_PUBLISHABLE_KEY")
)

if not db_url:
    raise RuntimeError("SUPABASE_URL is required")
if not db_key:
    raise RuntimeError(
        "SUPABASE_SERVICE_ROLE_KEY, SUPABASE_SECRET_KEY, or "
        "SUPABASE_PUBLISHABLE_KEY is required"
    )


client = create_client(db_url, db_key)
def get_or_create_supabase_client():
    return client
