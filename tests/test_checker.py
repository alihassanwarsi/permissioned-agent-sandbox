import pytest
from pydantic import BaseModel
from app.models.tool_spec import RiskLevel, ToolSpec
from app.models.user import Role, User
from app.permissions.checker import Decision, check_permission
from app.permissions.rate_limiter import RateLimiter

class DummySchema(BaseModel):
    pass

def make_user(role):
    return User(id="1", name="test", role=role)

def make_tool(risk, allowed_roles):
    return ToolSpec(
        name="x", description="x",
        input_schema=DummySchema, output_schema=DummySchema,
        handler=lambda x: x,
        allowed_roles=allowed_roles, rate_limit=100, risk_level=risk,
    )

def test_denied_when_role_not_allowed():
    user = make_user(Role.VIEWER)
    tool = make_tool(RiskLevel.LOW, allowed_roles=[Role.ADMIN])
    assert check_permission(user, tool, RateLimiter()).decision == Decision.DENIED

def test_low_risk_allowed_immediately():
    user = make_user(Role.VIEWER)
    tool = make_tool(RiskLevel.LOW, allowed_roles=[Role.VIEWER])
    assert check_permission(user, tool, RateLimiter()).decision == Decision.ALLOWED

def test_medium_risk_needs_confirmation():
    user = make_user(Role.ANALYST)
    tool = make_tool(RiskLevel.MEDIUM, allowed_roles=[Role.ANALYST])
    assert check_permission(user, tool, RateLimiter()).decision == Decision.NEEDS_CONFIRMATION

def test_high_risk_needs_approval():
    user = make_user(Role.ADMIN)
    tool = make_tool(RiskLevel.HIGH, allowed_roles=[Role.ADMIN])
    assert check_permission(user, tool, RateLimiter()).decision == Decision.NEEDS_APPROVAL

def test_rate_limited_when_calls_exceed_limit():
    user = make_user(Role.ADMIN)
    tool = ToolSpec(
        name="x", description="x",
        input_schema=DummySchema, output_schema=DummySchema,
        handler=lambda x: x,
        allowed_roles=[Role.ADMIN], rate_limit=1, risk_level=RiskLevel.LOW,
    )
    limiter = RateLimiter()
    limiter.record_call(user.id, tool.name)

    assert check_permission(user, tool, limiter).decision == Decision.RATE_LIMITED