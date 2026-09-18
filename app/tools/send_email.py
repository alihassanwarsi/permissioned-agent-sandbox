from pydantic import BaseModel, EmailStr
from app.models.user import Role
from app.models.tool_spec import RiskLevel, ToolSpec

class SendEmailInput(BaseModel):
    to: EmailStr
    subject: str
    body: str

class SendEmailOutput(BaseModel):
    status: str
    to: str
    subject: str

def send_email(input: SendEmailInput) -> SendEmailOutput:
    if not input.subject.strip():
        raise ValueError("subject cannot be empty")
    
    if not input.body.strip():
        raise ValueError("body cannot be empty.")

    print(f"[send_email mock] Would send to {input.to} | subject: {input.subject}")

    return SendEmailOutput(status="mocked", to=input.to, subject=input.subject)

send_email_tool = ToolSpec(
    name="send_email",
    description="Sends an email to a recipient.",
    input_schema=SendEmailInput,
    output_schema=SendEmailOutput,
    handler=send_email,
    allowed_roles=[Role.OPERATOR, Role.ADMIN],
    rate_limit=5,
    risk_level=RiskLevel.HIGH
)