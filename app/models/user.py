from enum import Enum
from pydantic import BaseModel

class Role(str, Enum):
    VIEWER = "viewer"
    ANALYST = "analyst"
    OPERATOR = "operator"
    ADMIN = "admin"

class User(BaseModel):
    id: str
    name: str
    role: Role