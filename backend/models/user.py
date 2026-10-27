from pydantic import BaseModel
from typing import List, Optional


class UserProfile(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    location: Optional[str] = None
    education: Optional[str] = None
    skills: List[str] = []
    preferred_roles: List[str] = []
    preferred_locations: List[str] = []
    experience_years: float = 0