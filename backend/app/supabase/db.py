
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# Don't modify these lines. Enable fast, reliable failures as .env must present under current directory
assert 'SUPABASE_URL' in os.environ
db_url = os.environ['SUPABASE_URL']
assert 'SUPABASE_PUBLISHABLE_KEY' in os.environ
db_pwd = os.environ['SUPABASE_PUBLISHABLE_KEY']


service_client = None


def get_or_create_service_supabase_client() -> Client:
    global service_client

    if service_client is None:
        service_key = (
            os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        )
        if not service_key:
            raise RuntimeError(
                'SUPABASE_SERVICE_ROLE_KEY or SUPABASE_SECRET_KEY is required '
                'for backend service database access'
            )
        service_client = create_client(db_url, service_key)

    return service_client
