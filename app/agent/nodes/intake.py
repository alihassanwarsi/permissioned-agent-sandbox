import uuid
from app.models.agent_state import AgentState
from app.models.user import User

def intake(user_message: str, user: User) -> AgentState:
    return AgentState(
        task_id=str(uuid.uuid4()),
        user_message=user_message,
        user=user
    )