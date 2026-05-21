
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

assert 'SUPABASE_URL' in os.environ
db_url = os.environ['SUPABASE_URL']
assert 'SUPABASE_PUBLISHABLE_KEY' in os.environ
db_pwd = os.environ['SUPABASE_PUBLISHABLE_KEY']


client = create_client(db_url, db_pwd)
def get_or_create_supabase_client():
    return client