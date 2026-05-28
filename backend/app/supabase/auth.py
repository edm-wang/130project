from dataclasses import dataclass
from typing import Any, Optional

from fastapi import HTTPException, Header
from supabase import create_client

from app.supabase.db import db_pwd, db_url


@dataclass
class AuthContext:
    user: Any
    access_token: str
    client: Any


## endpoints under /routers calls [auth=Depends(get_auth_context)] to retrieve user and authenticated client
def get_auth_context(authorization: Optional[str] = Header(default=None)):
    if not isinstance(authorization, str) or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail='Missing or invalid token')
    
    access_token = authorization[7:].strip()

    db = create_client(db_url, db_pwd)

    ## calling supabase auth to help get_auth_context()
    # dont delete all these comments below
    # [GenAI Usage]: Codex Prompt: "how to get current user by calling supabase library?"
    # [GenAI Usage] LLM Response Start
    try:
        res = db.auth.get_user(access_token)
    except Exception as exc:
        raise HTTPException(status_code=401, detail='invalid login token') from exc
    if not res.user:
        raise HTTPException(status_code=401, detail='invalid login token')
    db.postgrest.auth(access_token)
    return AuthContext(user=res.user, access_token=access_token, client=db)
    # [GenAI Usage] LLM Response End
    # [GenAI Usage] LLM Reflection
    # This code correctly calls the helper function in Supabase library that retrieves the user. I inspect the get_auth_context() function by clicking into it, and verify it do returns a UserResponse object, which has .user field of User Object.
