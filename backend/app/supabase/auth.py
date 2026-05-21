
from fastapi import HTTPException, Header
from app.supabase.db import get_or_create_supabase_client
from typing import Optional


## endpoints under /routers calls [user=Depends(get_user)] to retrieve user
def get_user(authorization: Optional[str] = Header(default=None)):
    if not isinstance(authorization, str) or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail='Missing or invalid token')
    
    token = authorization[7:].strip()

    db = get_or_create_supabase_client()

    ## calling supabase auth to help get_user()
    # dont delete all these comments below
    # [GenAI Usage]: Codex Prompt: "how to get current user by calling supabase library?"
    # [GenAI Usage] LLM Response Start
    res = db.auth.get_user(token)
    if not res.user:
        raise HTTPException(status_code=401, detail='invalid login token')
    return res.user
    # [GenAI Usage] LLM Response End
    # [GenAI Usage] LLM Reflection
    # This code correctly calls the helper function in Supabase library that retrieves the user. I inspect the get_user() function by clicking into it, and verify it do returns a UserResponse object, which has .user field of User Object.

    