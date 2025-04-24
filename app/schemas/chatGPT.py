from pydantic import BaseModel, Field


class AssistantRequest(BaseModel):
    message: str = Field(..., description="The message from the user to the assistant")


