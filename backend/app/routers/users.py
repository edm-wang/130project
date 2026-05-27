from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.supabase.auth import AuthContext, get_auth_context

users_router = APIRouter(prefix="/users")


class ProfileUpdate(BaseModel):
    display_name: Optional[str] = None
    institution: Optional[str] = None
    bio: Optional[str] = None


class InterestCreate(BaseModel):
    value: str
    interest_type: Literal["field", "topic", "author", "keyword", "category"]


@users_router.get("/me")
def get_profile(auth: AuthContext = Depends(get_auth_context)):
    client = auth.client
    user_id = str(auth.user.id)
    res = client.table("app_users").select("*").eq("id", user_id).execute()
    profile = res.data[0] if res.data else None
    return {"profile": profile}


@users_router.put("/me")
def save_profile(body: ProfileUpdate, auth: AuthContext = Depends(get_auth_context)):
    client = auth.client
    user_id = str(auth.user.id)
    payload = {
        "id": user_id,
        "email": auth.user.email,
        "onboarding_completed": True,
    }
    if body.display_name is not None:
        payload["display_name"] = body.display_name
    if body.institution is not None:
        payload["institution"] = body.institution
    if body.bio is not None:
        payload["bio"] = body.bio
    res = client.table("app_users").upsert(payload, on_conflict="id").execute()
    if not res.data:
        raise HTTPException(status_code=500, detail="Failed to save profile")
    return {"profile": res.data[0]}


@users_router.get("/me/interests")
def get_interests(auth: AuthContext = Depends(get_auth_context)):
    client = auth.client
    user_id = str(auth.user.id)
    res = (
        client.table("research_interests")
        .select("id, interest_type, value, preference_weight, created_at")
        .eq("user_id", user_id)
        .eq("is_active", True)
        .order("created_at")
        .execute()
    )
    return {"interests": res.data if res.data else []}


@users_router.post("/me/interests", status_code=201)
def add_interest(body: InterestCreate, auth: AuthContext = Depends(get_auth_context)):
    client = auth.client
    user_id = str(auth.user.id)
    value = body.value.strip()
    if not value:
        raise HTTPException(status_code=400, detail="value cannot be empty")
    res = (
        client.table("research_interests")
        .upsert(
            {
                "user_id": user_id,
                "interest_type": body.interest_type,
                "value": value,
                "normalized_value": value.lower(),
                "preference_weight": 1.0,
                "is_active": True,
            },
            on_conflict="user_id,interest_type,normalized_value",
        )
        .execute()
    )
    if not res.data:
        raise HTTPException(status_code=500, detail="Failed to add interest")
    return res.data[0]


@users_router.delete("/me/interests/{interest_id}", status_code=200)
def delete_interest(interest_id: str, auth: AuthContext = Depends(get_auth_context)):
    client = auth.client
    user_id = str(auth.user.id)
    res = (
        client.table("research_interests")
        .update({"is_active": False})
        .eq("id", interest_id)
        .eq("user_id", user_id)
        .execute()
    )
    if not res.data:
        raise HTTPException(status_code=404, detail="Interest not found")
    return {"deleted": interest_id}
