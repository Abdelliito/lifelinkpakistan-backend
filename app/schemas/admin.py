from pydantic import BaseModel


class PlatformStats(BaseModel):
    total_users: int
    total_donors: int
    available_donors: int
    active_requests: int
