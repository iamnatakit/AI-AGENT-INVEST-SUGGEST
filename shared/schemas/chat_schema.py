from pydantic import BaseModel
from typing import Optional

class ChatMessageCreate(BaseModel):
    message_id: str
    session_id: str
    user_id: str
    project_name: str
    role: str
    content: str
